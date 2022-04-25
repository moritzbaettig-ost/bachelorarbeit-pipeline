from filter import FilterPluginInterface


class Plugin(FilterPluginInterface):
    def filter_request(self, req: str) -> tuple[bool, str]:
        return (False, "")
