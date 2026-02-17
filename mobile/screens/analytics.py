"""
Analytics Screen for Procrastify
Focus score, app usage, and productivity insights
"""
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemLeadingIcon
from kivy.lang import Builder

Builder.load_string('''
<AnalyticsScreen>:
    name: "analytics"
    md_bg_color: app.theme_cls.backgroundColor
    
    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: "Analytics"
            type: "small"
            
            MDTopAppBarLeadingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "arrow-left"
                    on_release: app.go_to_screen('home')
                    
            MDTopAppBarTrailingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "refresh"
                    on_release: root.refresh_data()
                    
        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "16dp"
                spacing: "16dp"
                size_hint_y: None
                height: self.minimum_height
                
                # Focus Score Card
                MDCard:
                    orientation: "vertical"
                    padding: "24dp"
                    size_hint_y: None
                    height: "200dp"
                    style: "elevated"
                    md_bg_color: app.theme_cls.primaryContainerColor
                    
                    MDLabel:
                        text: "Today's Focus Score"
                        font_style: "Title"
                        role: "large"
                        halign: "center"
                        
                    MDLabel:
                        id: focus_score_label
                        text: "0%"
                        font_style: "Display"
                        role: "large"
                        halign: "center"
                        theme_text_color: "Custom"
                        text_color: app.theme_cls.primaryColor
                        
                    MDLabel:
                        id: focus_rating_label
                        text: "Start tracking!"
                        font_style: "Headline"
                        role: "small"
                        halign: "center"
                        
                    MDLabel:
                        id: focus_message_label
                        text: ""
                        font_style: "Body"
                        role: "medium"
                        halign: "center"
                        theme_text_color: "Secondary"
                        
                # Time Breakdown
                MDCard:
                    orientation: "vertical"
                    padding: "20dp"
                    size_hint_y: None
                    height: "180dp"
                    style: "elevated"
                    
                    MDLabel:
                        text: "Time Breakdown"
                        font_style: "Title"
                        role: "medium"
                        
                    MDBoxLayout:
                        size_hint_y: None
                        height: "100dp"
                        spacing: "16dp"
                        padding: 0, "16dp", 0, 0
                        
                        MDBoxLayout:
                            orientation: "vertical"
                            
                            MDLabel:
                                id: total_time_label
                                text: "0h 0m"
                                font_style: "Headline"
                                role: "medium"
                                halign: "center"
                                
                            MDLabel:
                                text: "Total Time"
                                font_style: "Body"
                                role: "small"
                                halign: "center"
                                theme_text_color: "Secondary"
                                
                        MDBoxLayout:
                            orientation: "vertical"
                            
                            MDLabel:
                                id: productive_label
                                text: "0h 0m"
                                font_style: "Headline"
                                role: "medium"
                                halign: "center"
                                theme_text_color: "Custom"
                                text_color: "#4CAF50"
                                
                            MDLabel:
                                text: "Productive"
                                font_style: "Body"
                                role: "small"
                                halign: "center"
                                theme_text_color: "Secondary"
                                
                        MDBoxLayout:
                            orientation: "vertical"
                            
                            MDLabel:
                                id: distraction_label
                                text: "0h 0m"
                                font_style: "Headline"
                                role: "medium"
                                halign: "center"
                                theme_text_color: "Custom"
                                text_color: "#F44336"
                                
                            MDLabel:
                                text: "Distracted"
                                font_style: "Body"
                                role: "small"
                                halign: "center"
                                theme_text_color: "Secondary"
                                
                # Top Apps Card
                MDCard:
                    orientation: "vertical"
                    padding: "16dp"
                    size_hint_y: None
                    height: "280dp"
                    style: "elevated"
                    
                    MDLabel:
                        text: "Top Apps Today"
                        font_style: "Title"
                        role: "medium"
                        size_hint_y: None
                        height: "32dp"
                        
                    ScrollView:
                        MDList:
                            id: apps_list
                            
                # Weekly Stats
                MDCard:
                    orientation: "vertical"
                    padding: "16dp"
                    size_hint_y: None
                    height: "200dp"
                    style: "elevated"
                    
                    MDLabel:
                        text: "This Week"
                        font_style: "Title"
                        role: "medium"
                        
                    MDBoxLayout:
                        size_hint_y: None
                        height: "120dp"
                        spacing: "8dp"
                        padding: 0, "16dp", 0, 0
                        
                        MDBoxLayout:
                            orientation: "vertical"
                            
                            MDLabel:
                                id: week_avg_label
                                text: "0%"
                                font_style: "Headline"
                                role: "medium"
                                halign: "center"
                                theme_text_color: "Custom"
                                text_color: app.theme_cls.primaryColor
                                
                            MDLabel:
                                text: "Avg Focus"
                                font_style: "Body"
                                role: "small"
                                halign: "center"
                                theme_text_color: "Secondary"
                                
                        MDBoxLayout:
                            orientation: "vertical"
                            
                            MDLabel:
                                id: week_productive_label
                                text: "0h"
                                font_style: "Headline"
                                role: "medium"
                                halign: "center"
                                
                            MDLabel:
                                text: "Productive"
                                font_style: "Body"
                                role: "small"
                                halign: "center"
                                theme_text_color: "Secondary"
                                
                        MDBoxLayout:
                            orientation: "vertical"
                            
                            MDLabel:
                                id: week_best_label
                                text: "-"
                                font_style: "Headline"
                                role: "medium"
                                halign: "center"
                                
                            MDLabel:
                                text: "Best Day"
                                font_style: "Body"
                                role: "small"
                                halign: "center"
                                theme_text_color: "Secondary"
''')


class AnalyticsScreen(MDScreen):
    """Analytics dashboard with focus scores and app usage"""
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh all analytics data"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        
        self.load_daily_analytics(app)
        self.load_weekly_analytics(app)
    
    def load_daily_analytics(self, app):
        """Load today's analytics"""
        result = app.api.get_daily_analytics()
        
        if result.get("success"):
            data = result.get("data", {})
            
            # Update focus score
            score = data.get("focus_score", 0)
            rating = data.get("focus_rating", "N/A")
            
            self.ids.focus_score_label.text = f"{score}%"
            self.ids.focus_rating_label.text = rating
            
            # Get focus message
            focus_result = app.api.get_focus_score()
            if focus_result.get("success"):
                message = focus_result.get("data", {}).get("message", "")
                self.ids.focus_message_label.text = message
            
            # Update time breakdown
            total = data.get("total_screen_time", 0)
            productive = data.get("productive_time", 0)
            distraction = data.get("distraction_time", 0)
            
            self.ids.total_time_label.text = self.format_time(total)
            self.ids.productive_label.text = self.format_time(productive)
            self.ids.distraction_label.text = self.format_time(distraction)
            
            # Update top apps
            self.load_top_apps(data.get("top_apps", []))
    
    def load_top_apps(self, apps):
        """Load top apps into list"""
        self.ids.apps_list.clear_widgets()
        
        if not apps:
            item = MDListItem(
                MDListItemLeadingIcon(icon="apps"),
                MDListItemHeadlineText(text="No app data yet"),
                MDListItemSupportingText(text="Start a focus session to track apps")
            )
            self.ids.apps_list.add_widget(item)
            return
        
        for app_data in apps[:5]:
            app_name = app_data.get("app_name", "Unknown")
            category = app_data.get("app_category", "neutral")
            seconds = app_data.get("total_seconds", 0)
            
            # Choose icon and color based on category
            if category == "productive":
                icon = "check-circle"
                color = "#4CAF50"
            elif category == "distraction":
                icon = "alert-circle"
                color = "#F44336"
            else:
                icon = "circle-outline"
                color = "#9E9E9E"
            
            item = MDListItem(
                MDListItemLeadingIcon(icon=icon, theme_icon_color="Custom", icon_color=color),
                MDListItemHeadlineText(text=app_name),
                MDListItemSupportingText(text=f"{self.format_time(seconds // 60)} • {category.title()}")
            )
            self.ids.apps_list.add_widget(item)
    
    def load_weekly_analytics(self, app):
        """Load weekly summary"""
        result = app.api.get_weekly_analytics()
        
        if result.get("success"):
            data = result.get("data", {})
            
            avg_focus = data.get("average_focus_score", 0)
            total_productive = data.get("total_productive_time", 0)
            best_day = data.get("best_day")
            
            self.ids.week_avg_label.text = f"{avg_focus}%"
            self.ids.week_productive_label.text = f"{total_productive // 60}h"
            
            if best_day:
                # Format date nicely
                date_str = best_day.get("date", "")
                if date_str:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(date_str)
                        self.ids.week_best_label.text = dt.strftime("%a")
                    except:
                        self.ids.week_best_label.text = date_str[:3]
            else:
                self.ids.week_best_label.text = "-"
    
    def format_time(self, minutes):
        """Format minutes to human readable string"""
        if minutes < 60:
            return f"{minutes}m"
        hours = minutes // 60
        mins = minutes % 60
        if mins:
            return f"{hours}h {mins}m"
        return f"{hours}h"
