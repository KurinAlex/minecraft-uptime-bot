import os


class Config:
    _cache = {}

    @classmethod
    def mc_server_host(cls) -> str:
        return cls._get_env_variable("MC_SERVER_HOST")

    @classmethod
    def mc_server_port(cls) -> int:
        return int(cls._get_env_variable("MC_SERVER_PORT"))

    @classmethod
    def bot_token(cls) -> str:
        return cls._get_env_variable("BOT_TOKEN")

    @classmethod
    def check_interval(cls) -> int:
        return int(cls._get_env_variable("CHECK_INTERVAL_SECONDS"))

    @staticmethod
    def _get_env_variable(name: str) -> str:
        if name in Config._cache:
            return Config._cache[name]

        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Environment variable '{name}' is required.")

        Config._cache[name] = value
        return value
