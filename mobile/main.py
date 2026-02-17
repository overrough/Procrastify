"""
Procrastify v2.0 - Mobile App
Main Entry Point with KivyMD Material Design
"""
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

# Import screens
from screens.login import LoginScreen
from screens.register import RegisterScreen
from screens.home import HomeScreen
from screens.tasks import TasksScreen
from screens.analytics import AnalyticsScreen
from screens.focus import FocusScreen
from screens.settings import SettingsScreen

# Import services
from services.api_client import APIClient

# Set window size for desktop testing (will be fullscreen on mobile)
Window.size = (400, 700)

# Main KV Layout
KV = '''
#:import get_color_from_hex kivy.utils.get_color_from_hex

<WindowManager>:
    LoginScreen:
    RegisterScreen:
    HomeScreen:
    TasksScreen:
    AnalyticsScreen:
    FocusScreen:
    SettingsScreen:

MDNavigationLayout:
    MDScreenManager:
        id: screen_manager
        
    MDNavigationDrawer:
        id: nav_drawer
        radius: [0, 16, 16, 0]
        
        MDNavigationDrawerMenu:
            MDNavigationDrawerHeader:
                title: "Procrastify"
                title_color: "#4CAF50"
                text: "Productivity Made Simple"
                spacing: "4dp"
                padding: "12dp", 0, 0, "56dp"
                
            MDNavigationDrawerItem:
                icon: "home"
                text: "Dashboard"
                on_release:
                    nav_drawer.set_state("close")
                    screen_manager.current = "home"
                    
            MDNavigationDrawerItem:
                icon: "checkbox-marked-outline"
                text: "Tasks"
                on_release:
                    nav_drawer.set_state("close")
                    screen_manager.current = "tasks"
                    
            MDNavigationDrawerItem:
                icon: "chart-line"
                text: "Analytics"
                on_release:
                    nav_drawer.set_state("close")
                    screen_manager.current = "analytics"
                    
            MDNavigationDrawerItem:
                icon: "timer"
                text: "Focus Timer"
                on_release:
                    nav_drawer.set_state("close")
                    screen_manager.current = "focus"
                    
            MDNavigationDrawerDivider:
            
            MDNavigationDrawerItem:
                icon: "cog"
                text: "Settings"
                on_release:
                    nav_drawer.set_state("close")
                    screen_manager.current = "settings"
                    
            MDNavigationDrawerItem:
                icon: "logout"
                text: "Logout"
                on_release:
                    app.logout()
'''


class WindowManager(ScreenManager):
    """Manages screen transitions"""
    pass


class ProcrastifyApp(MDApp):
    """Main Procrastify Application"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = APIClient()
        self.user = None
        self.token = None
    
    def build(self):
        """Build the application"""
        # Theme configuration
        self.theme_cls.theme_style = "Dark"  # Dark mode by default
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "LightGreen"
        self.theme_cls.material_style = "M3"
        
        # Set app title
        self.title = "Procrastify v2.0"
        
        # Create screen manager
        self.sm = ScreenManager(transition=SlideTransition())
        
        # Add screens
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(RegisterScreen(name='register'))
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(TasksScreen(name='tasks'))
        self.sm.add_widget(AnalyticsScreen(name='analytics'))
        self.sm.add_widget(FocusScreen(name='focus'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        
        return self.sm
    
    def login_user(self, user_data, token):
        """Set logged in user"""
        self.user = user_data
        self.token = token
        self.api.set_token(token)
        self.sm.current = 'home'
    
    def logout(self):
        """Logout user"""
        self.user = None
        self.token = None
        self.api.set_token(None)
        self.sm.current = 'login'
    
    def go_to_screen(self, screen_name):
        """Navigate to a screen"""
        self.sm.current = screen_name
    
    def show_snackbar(self, text):
        """Show a snackbar message"""
        from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
        MDSnackbar(
            MDSnackbarText(text=text),
            y="24dp",
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
        ).open()


if __name__ == '__main__':
    ProcrastifyApp().run()
