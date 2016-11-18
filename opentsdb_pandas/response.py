"""Response Module."""
import pandas
import logging

try:
    # Use ujson if available.
    import ujson as json
except ImportError:
    import json

log = logging.getLogger(__name__)


class OpenTSDBResponseSeries():
    """A single OpenTSDB response series i.e 1 element of the response array.

    Params:
        **kwargs : OpenTSDB response series data
    """

    def __init__(self, **kwargs):
        """Initialisation for OpenTSDBResponseSeries."""
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def id(self):
        """
        Id for series.

        Returns:
            metric{sorted=tag,key=value}
        """
        if len(self.tags.keys()) > 0:
            tags = ",".join(["%s=%s" %
                             (k, self.tags[k]) for k in
                             sorted(self.tags.keys())])
            return "%s{%s}" % (self.metric, tags)
        else:
            return self.metric

    def alias(self, func_or_str):
        """
        Generate aliases from OpenTSDB.

        User specified alias using lambda functions and string formatting
        using metadata provided by opentsdb.
        # TODO: Don't fail silently.
        This function fails silently.

        Args:
            func_or_str:    lambda function or python string format. When
                            using lambda functions,  they must begin with
                            '!' e.g. !lambda x: x....
        Return:
            Formatted alias on success and id or failure.
        """
        flat_data = self.__flattenedMetadata()
        # Normalized alias
        _alias = ""
        if func_or_str.startswith("!"):
            try:
                _alias = eval(func_or_str[1:])(flat_data)
            except Exception as e:
                log.info("Caught an exception generating alias. %r" % (e))
        else:
            try:
                _alias = func_or_str % (flat_data)
            except Exception as e:
                log.info("Caught an exception generating alias. %r" % (e))

        if _alias == "":
            return self.id

        return _alias

    def __flattened_metadata(self):
        """Flatten all metadata which is used for normalization."""
        return dict([("metric", self.metric)] +
                    [("tags.%s" % (k), v) for k, v in self.tags.items()])

    def datapoints(self, convert_time=False):
        """
        Convert datapoints.

        KWargs:
            convert_time: Whether to convert epoch to pandas datetime

        Return:
            Array of tuples (time, value)
        """
        if convert_time:
            return dict([(pandas.to_datetime(int(k), unit='s'), v)
                        for k, v in self.dps.items()])

        return dict([(int(k), v) for k, v in self.dps.items()])


class OpenTSDBResponse(object):
    """Complete OpenTSDB response."""

    def __init__(self, otsdb_resp):
        """Initialise an OpenTSDBResponse.

        Args:
            otsdb_resp: raw opentsdb response as a str, list or tuple.
        """
        if isinstance(otsdb_resp, str) or isinstance(otsdb_resp, unicode):
            # string response
            self._series = [OpenTSDBResponseSeries(
                **s) for s in json.loads(otsdb_resp)]
        elif isinstance(otsdb_resp, list) or isinstance(otsdb_resp, tuple):
            # dict response
            self._series = [OpenTSDBResponseSeries(**s) for s in otsdb_resp]
        else:
            raise RuntimeError("Invalid type: %s" % (type(otsdb_resp)))

    @property
    def series(self):
        """Use iterator for better memory management."""
        for s in self._series:
            yield s

    def data_frame(self, alias_transform=None, convert_time=False):
        """
        Convert an OpenTSDB array response into a DataFrame.

        KWargs:
            alias_transform: lambda function or string format to customize
                             serie name i.e. alias
            convert_time: Whether to convert epoch to pandas datetime

        Return:
            OpenTSDB response DataFrame
        """
        if alias_transform is None:
            return pandas.DataFrame(dict([
                (s.id, s.datapoints(convert_time)) for s in self.series]))
        else:
            return pandas.DataFrame(dict([
                (s.alias(alias_transform), s.datapoints(convert_time))
                for s in self.series]))
