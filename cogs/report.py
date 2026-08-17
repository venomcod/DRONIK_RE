import os
from datetime import timedelta
import discord
from discord.ext import commands

# ID канала по умолчанию для отправки жалоб
DEFAULT_REPORT_CHANNEL_ID = 1039855192281198593

# Список ID пользователей, которым разрешено принимать решения по жалобам (рассматривать кнопки)
ALLOWED_MODERATOR_IDS = {
    499507046681673728,
    695855560402403338
}


def is_moderator(member: discord.Member) -> bool:
    """Проверяет, разрешено ли пользователю принимать решения по жалобам."""
    return member.id in ALLOWED_MODERATOR_IDS or member == member.guild.owner


# --- Модальные окна для модераторов ---

class MuteModal(discord.ui.Modal, title="Выдать мут (таймаут)"):
    duration = discord.ui.TextInput(
        label="Длительность (в минутах или h/d)",
        placeholder="Например: 10, 30m, 2h, 1d",
        default="30m",
        max_length=20,
        required=True,
    )
    reason = discord.ui.TextInput(
        label="Причина наказания",
        style=discord.TextStyle.paragraph,
        placeholder="Укажите причину мута...",
        max_length=500,
        required=True,
    )

    def __init__(self, target_id: int, reporter_id: int):
        super().__init__()
        self.target_id = target_id
        self.reporter_id = reporter_id

    async def on_submit(self, interaction: discord.Interaction):
        await process_report_action(
            interaction=interaction,
            action_type="mute",
            target_id=self.target_id,
            reporter_id=self.reporter_id,
            reason=self.reason.value,
            duration_raw=self.duration.value,
        )


class KickModal(discord.ui.Modal, title="Исключить участника (Кик)"):
    reason = discord.ui.TextInput(
        label="Причина кика",
        style=discord.TextStyle.paragraph,
        placeholder="Укажите причину исключения...",
        max_length=500,
        required=True,
    )

    def __init__(self, target_id: int, reporter_id: int):
        super().__init__()
        self.target_id = target_id
        self.reporter_id = reporter_id

    async def on_submit(self, interaction: discord.Interaction):
        await process_report_action(
            interaction=interaction,
            action_type="kick",
            target_id=self.target_id,
            reporter_id=self.reporter_id,
            reason=self.reason.value,
        )


class BanModal(discord.ui.Modal, title="Заблокировать участника (Бан)"):
    reason = discord.ui.TextInput(
        label="Причина бана",
        style=discord.TextStyle.paragraph,
        placeholder="Укажите причину блокировки...",
        max_length=500,
        required=True,
    )

    def __init__(self, target_id: int, reporter_id: int):
        super().__init__()
        self.target_id = target_id
        self.reporter_id = reporter_id

    async def on_submit(self, interaction: discord.Interaction):
        await process_report_action(
            interaction=interaction,
            action_type="ban",
            target_id=self.target_id,
            reporter_id=self.reporter_id,
            reason=self.reason.value,
        )


class RejectModal(discord.ui.Modal, title="Отклонить жалобу"):
    reason = discord.ui.TextInput(
        label="Причина отказа",
        style=discord.TextStyle.paragraph,
        placeholder="Укажите причину отклонения жалобы (например: не найдено нарушений)...",
        max_length=500,
        required=True,
    )

    def __init__(self, target_id: int, reporter_id: int):
        super().__init__()
        self.target_id = target_id
        self.reporter_id = reporter_id

    async def on_submit(self, interaction: discord.Interaction):
        await process_report_action(
            interaction=interaction,
            action_type="reject",
            target_id=self.target_id,
            reporter_id=self.reporter_id,
            reason=self.reason.value,
        )


# --- Функция обработки решений модератора ---

def parse_duration(duration_str: str) -> timedelta | None:
    """Парсит строку длительности в timedelta."""
    s = duration_str.strip().lower()
    if not s:
        return None
    try:
        if s.endswith("d") or s.endswith("д"):
            days = float(s[:-1])
            return timedelta(days=days)
        if s.endswith("h") or s.endswith("ч"):
            hours = float(s[:-1])
            return timedelta(hours=hours)
        if s.endswith("m") or s.endswith("м"):
            minutes = float(s[:-1])
            return timedelta(minutes=minutes)
        if s.endswith("s") or s.endswith("с"):
            seconds = float(s[:-1])
            return timedelta(seconds=seconds)
        # Если просто число — считаем минутами
        minutes = float(s)
        return timedelta(minutes=minutes)
    except ValueError:
        return None


async def process_report_action(
    interaction: discord.Interaction,
    action_type: str,
    target_id: int,
    reporter_id: int,
    reason: str,
    duration_raw: str | None = None,
):
    guild = interaction.guild
    moderator = interaction.user
    target_member = guild.get_member(target_id)
    reporter_user = interaction.client.get_user(reporter_id) or await interaction.client.fetch_user(reporter_id)

    action_title = ""
    status_color = discord.Color.green()
    action_details_text = ""

    # 1. Применяем наказание на сервере
    if action_type == "mute":
        delta = parse_duration(duration_raw) if duration_raw else timedelta(minutes=30)
        if not delta or delta.total_seconds() <= 0:
            return await interaction.response.send_message(
                "❌ Некорректный формат времени. Используйте, например: `10m`, `2h`, `1d`.",
                ephemeral=True,
            )
        if delta > timedelta(days=28):
            return await interaction.response.send_message(
                "❌ Максимальная длительность мута в Discord — 28 дней.",
                ephemeral=True,
            )

        if not target_member:
            return await interaction.response.send_message(
                "❌ Пользователь не найден на сервере (возможно, покинул сервер).",
                ephemeral=True,
            )

        try:
            await target_member.timeout(delta, reason=f"[Жалоба] {reason} (Модератор: {moderator})")
            action_title = f"🔇 Наказание: Мут на {duration_raw}"
            action_details_text = f"Выдан мут на **{duration_raw}**"
            status_color = discord.Color.orange()
        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ У бота нет прав для выдачи мута этому пользователю.", ephemeral=True
            )
        except Exception as exc:
            return await interaction.response.send_message(
                f"❌ Ошибка при выдаче мута: {exc}", ephemeral=True
            )

    elif action_type == "kick":
        if not target_member:
            return await interaction.response.send_message(
                "❌ Пользователь не найден на сервере.", ephemeral=True
            )
        try:
            # Уведомляем нарушителя до кика
            try:
                dm_embed = discord.Embed(
                    title=f"👞 Вы были исключены с сервера {guild.name}",
                    description=f"**Причина:** {reason}\n**Модератор:** {moderator.name}",
                    color=discord.Color.red(),
                )
                await target_member.send(embed=dm_embed)
            except Exception:
                pass

            await target_member.kick(reason=f"[Жалоба] {reason} (Модератор: {moderator})")
            action_title = "👞 Наказание: Кик"
            action_details_text = "Пользователь исключен с сервера"
            status_color = discord.Color.red()
        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ У бота нет прав для исключения этого пользователя.", ephemeral=True
            )
        except Exception as exc:
            return await interaction.response.send_message(
                f"❌ Ошибка при исключении: {exc}", ephemeral=True
            )

    elif action_type == "ban":
        try:
            # Уведомляем нарушителя до бана
            if target_member:
                try:
                    dm_embed = discord.Embed(
                        title=f"⛔ Вы были заблокированы на сервере {guild.name}",
                        description=f"**Причина:** {reason}\n**Модератор:** {moderator.name}",
                        color=discord.Color.dark_red(),
                    )
                    await target_member.send(embed=dm_embed)
                except Exception:
                    pass

            await guild.ban(
                discord.Object(id=target_id),
                reason=f"[Жалоба] {reason} (Модератор: {moderator})",
            )
            action_title = "⛔ Наказание: Бан"
            action_details_text = "Пользователь заблокирован на сервере"
            status_color = discord.Color.dark_red()
        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ У бота нет прав для бана этого пользователя.", ephemeral=True
            )
        except Exception as exc:
            return await interaction.response.send_message(
                f"❌ Ошибка при блокировке: {exc}", ephemeral=True
            )

    elif action_type == "reject":
        action_title = "❌ Жалоба отклонена"
        action_details_text = "Нарушений не обнаружено / Отказ"
        status_color = discord.Color.light_grey()

    # 2. Отправка уведомления нарушителю в ЛС (для мута)
    if action_type == "mute" and target_member:
        try:
            dm_embed = discord.Embed(
                title=f"🔇 Вам выдан мут на сервере {guild.name}",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow(),
            )
            dm_embed.add_field(name="Длительность", value=duration_raw, inline=True)
            dm_embed.add_field(name="Причина", value=reason, inline=False)
            await target_member.send(embed=dm_embed)
        except Exception:
            pass

    # 3. Отправка уведомления автору жалобы в ЛС
    if reporter_user:
        try:
            dm_embed = discord.Embed(
                title=f"📋 Результат рассмотрения вашей жалобы ({guild.name})",
                color=status_color,
                timestamp=discord.utils.utcnow(),
            )
            dm_embed.add_field(
                name="Статус",
                value="✅ Принята" if action_type != "reject" else "❌ Отклонена",
                inline=False,
            )
            dm_embed.add_field(name="Решение модератора", value=action_title, inline=False)
            dm_embed.add_field(name="Комментарий / Причина", value=reason, inline=False)
            dm_embed.set_footer(text=f"Модератор: {moderator.display_name}")
            await reporter_user.send(embed=dm_embed)
        except Exception:
            pass

    # 4. Обновление Embed'а в канале жалоб
    original_message = interaction.message
    if original_message and original_message.embeds:
        embed = original_message.embeds[0]
        embed.color = status_color
        embed.title = f"📁 Жалоба рассмотрена — {action_title}"
        embed.add_field(
            name="⚖️ Решение модератора",
            value=f"**Модератор:** {moderator.mention}\n**Вердикт:** {action_details_text}\n**Причина решения:** {reason}",
            inline=False,
        )

        # Отключаем кнопки
        view = discord.ui.View.from_message(original_message)
        for child in view.children:
            child.disabled = True

        await interaction.response.edit_message(embed=embed, view=view)
    else:
        await interaction.response.send_message("✅ Решение принято.", ephemeral=True)


# --- View с кнопками для модераторов ---

class ReportActionView(discord.ui.View):
    def __init__(self, target_id: int, reporter_id: int):
        super().__init__(timeout=None)  # Постоянная View без таймаута
        self.target_id = target_id
        self.reporter_id = reporter_id

    async def _check_perms(self, interaction: discord.Interaction) -> bool:
        if not is_moderator(interaction.user):
            await interaction.response.send_message(
                "❌ У вас нет прав модератора для рассмотрения жалоб.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Мут", style=discord.ButtonStyle.secondary, emoji="🔇")
    async def mute_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_perms(interaction):
            return
        modal = MuteModal(target_id=self.target_id, reporter_id=self.reporter_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Кик", style=discord.ButtonStyle.primary, emoji="👞")
    async def kick_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_perms(interaction):
            return
        modal = KickModal(target_id=self.target_id, reporter_id=self.reporter_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Бан", style=discord.ButtonStyle.danger, emoji="⛔")
    async def ban_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_perms(interaction):
            return
        modal = BanModal(target_id=self.target_id, reporter_id=self.reporter_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Отклонить", style=discord.ButtonStyle.grey, emoji="❌")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_perms(interaction):
            return
        modal = RejectModal(target_id=self.target_id, reporter_id=self.reporter_id)
        await interaction.response.send_modal(modal)


# --- Модальное окно и кнопки для пользователей ---

class ReportModal(discord.ui.Modal, title="Жалоба на участника"):
    reason = discord.ui.TextInput(
        label="Причина жалобы",
        placeholder="Кратко укажите причину (например, оскорбления, спам)",
        max_length=100,
        required=True,
    )
    details = discord.ui.TextInput(
        label="Подробное описание и доказательства",
        style=discord.TextStyle.paragraph,
        placeholder="Опишите ситуацию подробнее, при необходимости укажите ссылки на доказательства...",
        max_length=1024,
        required=True,
    )

    def __init__(self, target_member: discord.Member, channel_id: int):
        super().__init__()
        self.target_member = target_member
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        report_channel = interaction.guild.get_channel(self.channel_id)
        if not isinstance(report_channel, discord.TextChannel):
            await interaction.response.send_message(
                "❌ Ошибка: канал для жалоб не найден или не настроен.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="🚨 Новая жалоба на пользователя",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=self.target_member.display_avatar.url)
        embed.add_field(
            name="👤 Нарушитель",
            value=f"{self.target_member.mention} (`{self.target_member.name}` | ID: `{self.target_member.id}`)",
            inline=False,
        )
        embed.add_field(
            name="👮 Автор жалобы",
            value=f"{interaction.user.mention} (`{interaction.user.name}` | ID: `{interaction.user.id}`)",
            inline=False,
        )
        embed.add_field(
            name="📌 Причина",
            value=self.reason.value,
            inline=False,
        )
        embed.add_field(
            name="📝 Описание / Доказательства",
            value=self.details.value,
            inline=False,
        )
        if interaction.channel:
            embed.add_field(
                name="📍 Канал обращения",
                value=interaction.channel.mention,
                inline=False,
            )
        embed.set_footer(
            text=f"ID автора: {interaction.user.id} • ID нарушителя: {self.target_member.id}",
            icon_url=interaction.user.display_avatar.url,
        )

        admin_view = ReportActionView(
            target_id=self.target_member.id,
            reporter_id=interaction.user.id,
        )

        try:
            await report_channel.send(embed=embed, view=admin_view)
            await interaction.response.send_message(
                f"✅ Ваша жалоба на {self.target_member.mention} успешно отправлена модераторам.",
                ephemeral=True,
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ У бота нет прав для отправки сообщения в канал жалоб.",
                ephemeral=True,
            )
        except Exception as exc:
            await interaction.response.send_message(
                f"❌ Произошла ошибка при отправке жалобы: {exc}",
                ephemeral=True,
            )


class ReportButtonView(discord.ui.View):
    def __init__(self, target_member: discord.Member, author_id: int, channel_id: int):
        super().__init__(timeout=180)
        self.target_member = target_member
        self.author_id = author_id
        self.channel_id = channel_id

    @discord.ui.button(label="Заполнить жалобу", style=discord.ButtonStyle.danger, emoji="📝")
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "❌ Только автор команды может открыть эту форму.",
                ephemeral=True,
            )
            return

        modal = ReportModal(target_member=self.target_member, channel_id=self.channel_id)
        await interaction.response.send_modal(modal)


class Report(commands.Cog):
    """Ког для отправки и обработки жалоб на пользователей."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.report_channel_id = int(os.getenv("REPORT_CHANNEL_ID", DEFAULT_REPORT_CHANNEL_ID))

    @commands.hybrid_command(name="report", description="Отправить жалобу на участника сервера")
    async def report(self, ctx: commands.Context, member: discord.Member):
        """Открывает форму подачи жалобы на выбранного участника."""
        if member == ctx.author:
            return await ctx.send("Вы не можете отправить жалобу на самого себя.", ephemeral=True)
        if member.bot:
            return await ctx.send("Нельзя отправлять жалобу на бота.", ephemeral=True)

        if ctx.interaction is not None:
            # Если вызов через слэш-команду (/report)
            modal = ReportModal(target_member=member, channel_id=self.report_channel_id)
            await ctx.interaction.response.send_modal(modal)
        else:
            # Если вызов через текстовый префикс (!report @user)
            view = ReportButtonView(
                target_member=member,
                author_id=ctx.author.id,
                channel_id=self.report_channel_id,
            )
            await ctx.send(
                f"{ctx.author.mention}, нажмите кнопку ниже, чтобы открыть форму жалобы на {member.mention}:",
                view=view,
                delete_after=180,
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Report(bot))
