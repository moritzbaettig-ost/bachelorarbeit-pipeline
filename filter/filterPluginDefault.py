from filter import FilterPluginInterface


class Plugin(FilterPluginInterface):
    def filter_request(self, req: str) -> str:
        return req
