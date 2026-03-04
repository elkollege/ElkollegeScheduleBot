import aiogram
import pyquoks.services.logger


class LoggerService(pyquoks.services.logger.LoggerService):
    def log_user_interaction(self, user: aiogram.types.User, interaction: str) -> None:
        user_info = " ".join([
            " | ".join(i for i in [
                user.full_name,
                f"@{user.username}" if user.username else None,
            ] if i),
            f"({user.id})",
        ])

        self.info(f"{user_info} - \"{interaction}\"")
