"""
Settings Screen for Procrastify
Theme, notifications, and app preferences
"""
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder

Builder.load_string('''
<SettingsScreen>:
    name: "settings"
    md_bg_color: app.theme_cls.backgroundColor
    
    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: "Settings"
            type: "small"
            
            MDTopAppBarLeadingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "arrow-left"
                    on_release: app.go_to_screen('home')
                    
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "16dp"
                spacing: "8dp"
                size_hint_y: None
                height: self.minimum_height
                
                # Profile Section
                MDCard:
                    orientation: "vertical"
                    padding: "16dp"
                    size_hint_y: None
                    height: "120dp"
                    style: "elevated"
                    
                    MDBoxLayout:
                        spacing: "16dp"
                        
                        MDIcon:
                            icon: "account-circle"
                            font_size: "64sp"
                            theme_icon_color: "Custom"
                            icon_color: app.theme_cls.primaryColor
                            size_hint: None, None
                            size: "64dp", "64dp"
                            
                        MDBoxLayout:
                            orientation: "vertical"
                            spacing: "4dp"
                            
                            MDLabel:
                                id: name_label
                                text: "User Name"
                                font_style: "Headline"
                                role: "small"
                                
                            MDLabel:
                                id: email_label
                                text: "user@email.com"
                                font_style: "Body"
                                role: "medium"
                                theme_text_color: "Secondary"
                                
                # Appearance Section
                MDLabel:
                    text: "Appearance"
                    font_style: "Title"
                    role: "small"
                    padding: "8dp", "16dp", "8dp", "8dp"
                    size_hint_y: None
                    height: self.texture_size[1]
                    theme_text_color: "Secondary"
                    
                MDCard:
                    orientation: "vertical"
                    padding: "0dp"
                    size_hint_y: None
                    height: "60dp"
                    style: "outlined"
                    
                    MDListItem:
                        on_release: root.toggle_theme()
                        
                        MDListItemLeadingIcon:
                            icon: "theme-light-dark"
                            
                        MDListItemHeadlineText:
                            text: "Dark Mode"
                            
                        MDListItemTrailingIcon:
                            id: theme_icon
                            icon: "toggle-switch"
                            theme_icon_color: "Custom"
                            icon_color: app.theme_cls.primaryColor
                            
                # Focus Settings
                MDLabel:
                    text: "Focus Settings"
                    font_style: "Title"
                    role: "small"
                    padding: "8dp", "16dp", "8dp", "8dp"
                    size_hint_y: None
                    height: self.texture_size[1]
                    theme_text_color: "Secondary"
                    
                MDCard:
                    orientation: "vertical"
                    padding: "0dp"
                    size_hint_y: None
                    height: "180dp"
                    style: "outlined"
                    
                    MDListItem:
                        MDListItemLeadingIcon:
                            icon: "timer"
                            
                        MDListItemHeadlineText:
                            text: "Focus Duration"
                            
                        MDListItemSupportingText:
                            text: "25 minutes"
                            
                    MDDivider:
                    
                    MDListItem:
                        MDListItemLeadingIcon:
                            icon: "coffee"
                            
                        MDListItemHeadlineText:
                            text: "Break Duration"
                            
                        MDListItemSupportingText:
                            text: "5 minutes"
                            
                    MDDivider:
                    
                    MDListItem:
                        MDListItemLeadingIcon:
                            icon: "alert"
                            
                        MDListItemHeadlineText:
                            text: "Distraction Alert Threshold"
                            
                        MDListItemSupportingText:
                            text: "5 minutes"
                            
                # About Section
                MDLabel:
                    text: "About"
                    font_style: "Title"
                    role: "small"
                    padding: "8dp", "16dp", "8dp", "8dp"
                    size_hint_y: None
                    height: self.texture_size[1]
                    theme_text_color: "Secondary"
                    
                MDCard:
                    orientation: "vertical"
                    padding: "0dp"
                    size_hint_y: None
                    height: "120dp"
                    style: "outlined"
                    
                    MDListItem:
                        MDListItemLeadingIcon:
                            icon: "information"
                            
                        MDListItemHeadlineText:
                            text: "Version"
                            
                        MDListItemSupportingText:
                            text: "2.0.0"
                            
                    MDDivider:
                    
                    MDListItem:
                        MDListItemLeadingIcon:
                            icon: "github"
                            
                        MDListItemHeadlineText:
                            text: "Built by"
                            
                        MDListItemSupportingText:
                            text: "BCA G39 Team"
                            
                # Logout Button
                MDBoxLayout:
                    size_hint_y: None
                    height: "80dp"
                    padding: "16dp"
                    
                    MDButton:
                        style: "outlined"
                        size_hint_x: 1
                        on_release: app.logout()
                        theme_line_color: "Custom"
                        line_color: "#F44336"
                        
                        MDButtonIcon:
                            icon: "logout"
                            theme_icon_color: "Custom"
                            icon_color: "#F44336"
                            
                        MDButtonText:
                            text: "LOGOUT"
                            theme_text_color: "Custom"
                            text_color: "#F44336"
''')


class SettingsScreen(MDScreen):
    """Settings screen for app preferences"""
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.load_profile()
        self.update_theme_icon()
    
    def load_profile(self):
        """Load user profile"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        if app.user:
            self.ids.name_label.text = app.user.get("name", "User")
            self.ids.email_label.text = app.user.get("email", "")
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        if app.theme_cls.theme_style == "Dark":
            app.theme_cls.theme_style = "Light"
        else:
            app.theme_cls.theme_style = "Dark"
        
        self.update_theme_icon()
    
    def update_theme_icon(self):
        """Update theme toggle icon"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        if app.theme_cls.theme_style == "Dark":
            self.ids.theme_icon.icon = "toggle-switch"
        else:
            self.ids.theme_icon.icon = "toggle-switch-off"
