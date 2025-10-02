import asyncio
import httpx
import random
import time
import psutil
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from fake_useragent import UserAgent
from typing import List, Dict, Optional
import json

# استيراد الكلاسات الأساسية من البوت السابق (نفس الكود السابق)
class AdvancedBrowserSimulator:
    def __init__(self):
        self.ua = UserAgent()
        self.device_profiles = {
            'desktop': [
                {
                    'viewport': {'width': 1920, 'height': 1080},
                    'platform': 'Windows NT 10.0; Win64; x64',
                    'memory': 8,
                    'concurrency': 8
                }
            ],
            'mobile': [
                {
                    'viewport': {'width': 390, 'height': 844},
                    'platform': 'iPhone; CPU iPhone OS 17_1_1 like Mac OS X',
                    'memory': 4,
                    'concurrency': 6
                }
            ]
        }
        self.languages = ['en-US,en;q=0.9', 'ar-SA,ar;q=0.9,en;q=0.8']
        self.timezones = ['America/New_York', 'Europe/London', 'Asia/Dubai']

    def generate_browser_profile(self):
        device_type = 'mobile' if random.random() < 0.4 else 'desktop'
        device_profile = random.choice(self.device_profiles[device_type])
        
        return {
            'user_agent': self.ua.random,
            'viewport': device_profile['viewport'],
            'device_type': device_type,
            'language': random.choice(self.languages),
            'timezone': random.choice(self.timezones),
            'platform': device_profile['platform'],
            'hardware_concurrency': device_profile['concurrency'],
            'device_memory': device_profile['memory']
        }

class AdvancedVisitBot:
    def __init__(self, telegram_app=None):
        self.is_running = False
        self.stats = {
            'successful_visits': 0,
            'failed_visits': 0,
            'total_attempted': 0,
            'auto_fixed_errors': 0,
            'proxy_rotations': 0,
            'concurrent_tasks': 0,
            'errors_log': []
        }
        self.target_url = ""
        self.desired_visits = 0
        self.current_session_id = None
        self.browser_simulator = AdvancedBrowserSimulator()
        self.semaphore_value = 50
        self.semaphore = asyncio.Semaphore(self.semaphore_value)
        self.telegram_app = telegram_app
        self.stats_interval = 100  # الإفتراضي: إرسال إحصائيات كل 100 زيارة ناجحة
        
        # إعدادات البروكسي
        self.proxy_config = {
            'username': 'yahia_FwOsV',
            'password': 'Yahia+14118482',
            'entry_point': 'pr.oxylabs.io:7777'
        }
        self.countries = ['US', 'GB', 'CA', 'DE', 'FR', 'JP', 'SG', 'AU', 'NL', 'SE']

    async def send_telegram_message(self, chat_id, message):
        """إرسال رسالة إلى Telegram"""
        if self.telegram_app:
            try:
                await self.telegram_app.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='HTML'
                )
            except Exception as e:
                print(f"خطأ في إرسال رسالة Telegram: {e}")

    async def make_async_request(self, client: httpx.AsyncClient, url: str, visit_number: int) -> tuple:
        """إجراء طلب HTTP مع نظام الإصلاح التلقائي"""
        try:
            browser_profile = self.browser_simulator.generate_browser_profile()
            proxy_url = self.generate_proxy_url()
            
            headers = {
                'User-Agent': browser_profile['user_agent'],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': browser_profile['language'],
                'Accept-Encoding': 'gzip, deflate, br',
            }
            
            response = await client.get(
                url,
                headers=headers,
                proxies={"http://": proxy_url, "https://": proxy_url},
                timeout=30.0,
                follow_redirects=True
            )
            
            await asyncio.sleep(random.uniform(2, 5))
            
            if response.status_code == 200:
                # إرسال إحصائيات تلقائية كل عدد محدد من الزيارات الناجحة
                if self.stats['successful_visits'] % self.stats_interval == 0 and self.stats['successful_visits'] > 0:
                    stats_msg = self.create_stats_message()
                    # إرسال للإدمن فقط - يمكنك تعديل chat_id حسب الحاجة
                    await self.send_telegram_message("YOUR_CHAT_ID", stats_msg)
                
                return True, "نجاح"
            else:
                return False, f"خطأ HTTP: {response.status_code}"
                
        except Exception as e:
            return False, f"خطأ اتصال: {str(e)}"

    def create_stats_message(self):
        """إنشاء رسالة الإحصائيات"""
        success_rate = (self.stats['successful_visits'] / self.stats['total_attempted'] * 100) if self.stats['total_attempted'] > 0 else 0
        progress = (self.stats['total_attempted'] / self.desired_visits * 100) if self.desired_visits > 0 else 0
        
        return f"""📊 <b>الإحصائيات التلقائية</b>
        
🎯 التقدم: <code>{progress:.1f}%</code>
✅ الزيارات الناجحة: <code>{self.stats['successful_visits']:,}</code>
❌ الزيارات الفاشلة: <code>{self.stats['failed_visits']:,}</code>
📈 معدل النجاح: <code>{success_rate:.1f}%</code>
🔄 الأخطاء المصلحة: <code>{self.stats['auto_fixed_errors']:,}</code>
🌍 دورات البروكسي: <code>{self.stats['proxy_rotations']:,}</code>

⚙️ الإعداد: إرسال إحصائيات كل <code>{self.stats_interval}</code> زيارة ناجحة"""

    def generate_proxy_url(self, country: str = None):
        if country is None:
            country = random.choice(self.countries)
        return (f'http://customer-{self.proxy_config["username"]}-cc-{country}:'
                f'{self.proxy_config["password"]}@{self.proxy_config["entry_point"]}')

    async def visit_task(self, client: httpx.AsyncClient, visit_number: int):
        async with self.semaphore:
            self.stats['concurrent_tasks'] = self.semaphore_value - self.semaphore._value
            
            success, message = await self.make_async_request(client, self.target_url, visit_number)
            
            if success:
                self.stats['successful_visits'] += 1
            else:
                self.stats['failed_visits'] += 1
            
            self.stats['total_attempted'] += 1

    async def start_campaign(self, url: str, visits: int = 5000):
        if self.is_running:
            return False, "البوت يعمل بالفعل!"
        
        self.target_url = url
        self.desired_visits = visits
        self.is_running = True
        
        async with httpx.AsyncClient() as client:
            tasks = []
            for i in range(1, self.desired_visits + 1):
                if not self.is_running:
                    break
                task = asyncio.create_task(self.visit_task(client, i))
                tasks.append(task)
                if i % 20 == 0:
                    await asyncio.sleep(0.1)
            
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.is_running = False
        return True, f"اكتملت الحملة: {self.stats['successful_visits']} نجاح من {self.stats['total_attempted']} محاولة"

    def set_stats_interval(self, interval: int):
        """تحديد الفترة الزمنية للإحصائيات التلقائية"""
        if interval < 10:
            return "❌ الحد الأدنى للفترة هو 10 زيارات"
        self.stats_interval = interval
        return f"✅ تم ضبط إرسال الإحصائيات كل {interval} زيارة ناجحة"

    def get_stats(self):
        """جلب الإحصائيات الحالية"""
        success_rate = (self.stats['successful_visits'] / self.stats['total_attempted'] * 100) if self.stats['total_attempted'] > 0 else 0
        progress = (self.stats['total_attempted'] / self.desired_visits * 100) if self.desired_visits > 0 else 0
        
        return f"""📊 <b>إحصائيات البوت</b>

🎯 التقدم: <code>{progress:.1f}%</code>
✅ النجاح: <code>{self.stats['successful_visits']:,}</code>
❌ الفشل: <code>{self.stats['failed_visits']:,}</code>
📈 معدل النجاح: <code>{success_rate:.1f}%</code>
🔄 الأخطاء المصلحة: <code>{self.stats['auto_fixed_errors']:,}</code>
🌍 دورات البروكسي: <code>{self.stats['proxy_rotations']:,}</code>
⚡ العمليات النشطة: <code>{self.stats['concurrent_tasks']}</code>

⚙️ الإعداد الحالي: إرسال إحصائيات تلقائية كل <code>{self.stats_interval}</code> زيارة ناجحة"""

# نظام أوامر Telegram
class TelegramBotHandler:
    def __init__(self, token: str):
        self.token = token
        self.visit_bot = AdvancedVisitBot()
        self.application = None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر بدء البوت"""
        await update.message.reply_text(
            "🤖 <b>بوت الزيارات المتطور</b>\n\n"
            "استخدم /help لعرض جميع الأوامر المتاحة",
            parse_mode='HTML'
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر المساعدة"""
        help_text = """
🛠 <b>قائمة أوامر البوت:</b>

🔹 <b>الأوامر الأساسية:</b>
/start - بدء البوت
/help - عرض هذه القائمة
/stats - عرض الإحصائيات الحالية

🔹 <b>أوامر التشغيل:</b>
/start_campaign [رابط] [عدد الزيارات] - بدء حملة زيارات
/stop_campaign - إيقاف الحملة

🔹 <b>أوامر الإحصائيات:</b>
/set_interval [عدد] - تحديد عدد الزيارات لإرسال الإحصائيات تلقائياً
/current_interval - عرض الإعداد الحالي

🔹 <b>أوامر متقدمة:</b>
/semaphore [عدد] - تغيير عدد العمليات المتوازية
/resources - عرض استهلاك الموارد

📝 <b>أمثلة:</b>
/start_campaign https://example.com 5000
/set_interval 250
/semaphore 100
"""
        await update.message.reply_text(help_text, parse_mode='HTML')

    async def start_campaign_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر بدء حملة الزيارات"""
        if len(context.args) < 1:
            await update.message.reply_text(
                "❌ <b>استخدام:</b> /start_campaign [رابط] [عدد الزيارات - اختياري]\n"
                "📝 <b>مثال:</b> /start_campaign https://example.com 5000",
                parse_mode='HTML'
            )
            return

        url = context.args[0]
        visits = 5000
        if len(context.args) > 1:
            try:
                visits = int(context.args[1])
            except ValueError:
                await update.message.reply_text("⚠️ استخدام العدد الافتراضي 5000")

        # تحديث reference للبوت الرئيسي
        self.visit_bot.telegram_app = self.application
        self.visit_bot.stats_interval = self.visit_bot.stats_interval

        await update.message.reply_text(
            f"🚀 <b>بدء حملة الزيارات:</b>\n"
            f"🌐 <b>الرابط:</b> {url}\n"
            f"🎯 <b>الهدف:</b> {visits:,} زيارة\n"
            f"📊 <b>الإحصائيات:</b> كل {self.visit_bot.stats_interval} زيارة ناجحة\n\n"
            f"⏳ جاري البدء...",
            parse_mode='HTML'
        )

        # تشغيل الحملة في الخلفية
        success, message = await self.visit_bot.start_campaign(url, visits)
        
        await update.message.reply_text(
            f"{'✅' if success else '❌'} <b>{message}</b>",
            parse_mode='HTML'
        )

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر عرض الإحصائيات"""
        stats_text = self.visit_bot.get_stats()
        await update.message.reply_text(stats_text, parse_mode='HTML')

    async def set_interval_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تحديد فترة الإحصائيات التلقائية"""
        if len(context.args) < 1:
            await update.message.reply_text(
                "❌ <b>استخدام:</b> /set_interval [عدد الزيارات]\n"
                "📝 <b>مثال:</b> /set_interval 100",
                parse_mode='HTML'
            )
            return

        try:
            interval = int(context.args[0])
            result = self.visit_bot.set_stats_interval(interval)
            await update.message.reply_text(f"✅ {result}", parse_mode='HTML')
        except ValueError:
            await update.message.reply_text("❌ يرجى إدخال رقم صحيح", parse_mode='HTML')

    async def current_interval_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض الإعداد الحالي لفترة الإحصائيات"""
        await update.message.reply_text(
            f"⚙️ <b>الإعداد الحالي:</b> إرسال إحصائيات تلقائية كل "
            f"<code>{self.visit_bot.stats_interval}</code> زيارة ناجحة",
            parse_mode='HTML'
        )

    async def semaphore_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تغيير عدد العمليات المتوازية"""
        if len(context.args) < 1:
            await update.message.reply_text(
                "❌ <b>استخدام:</b> /semaphore [عدد العمليات]\n"
                "📝 <b>مثال:</b> /semaphore 100",
                parse_mode='HTML'
            )
            return

        try:
            new_value = int(context.args[0])
            if new_value <= 0:
                await update.message.reply_text("❌ يجب أن يكون الرقم أكبر من الصفر", parse_mode='HTML')
                return
            
            self.visit_bot.semaphore_value = new_value
            self.visit_bot.semaphore = asyncio.Semaphore(new_value)
            await update.message.reply_text(
                f"✅ تم تعديل عدد العمليات المتوازية إلى: <code>{new_value}</code>",
                parse_mode='HTML'
            )
        except ValueError:
            await update.message.reply_text("❌ يرجى إدخال رقم صحيح", parse_mode='HTML')

    def setup_handlers(self):
        """إعداد معالجات الأوامر"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("start_campaign", self.start_campaign_command))
        self.application.add_handler(CommandHandler("set_interval", self.set_interval_command))
        self.application.add_handler(CommandHandler("current_interval", self.current_interval_command))
        self.application.add_handler(CommandHandler("semaphore", self.semaphore_command))

    async def run(self):
        """تشغيل بوت Telegram"""
        self.application = Application.builder().token(self.token).build()
        self.visit_bot.telegram_app = self.application
        
        self.setup_handlers()
        
        print("🚀 بوت Telegram يعمل الآن...")
        await self.application.run_polling()

# التشغيل الرئيسي
async def main():
    # توكن بوت Telegram الخاص بك
    TELEGRAM_BOT_TOKEN = "8121636489:AAGMJcwUhHi-Bk0TDhSrIvASNPaSoF4XZjk"
    
    telegram_bot = TelegramBotHandler(TELEGRAM_BOT_TOKEN)
    await telegram_bot.run()

if __name__ == "__main__":
    asyncio.run(main())
