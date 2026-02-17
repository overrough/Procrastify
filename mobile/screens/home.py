"""
Home Dashboard Screen for Procrastify
Shows focus score, priority tasks, and quick stats
"""
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDListItemLeadingIcon
from kivy.lang import Builder
from kivy.clock import Clock

Builder.load_string('''
<HomeScreen>:
    name: "home"
    md_bg_color: app.theme_cls.backgroundColor
    
    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: "Procrastify"
            type: "small"
            
            MDTopAppBarLeadingButtonContainer:
                MDActionTopAppBarButton:
                    icon: "menu"
                    
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
                
                # Welcome Card
                MDCard:
                    orientation: "vertical"
                    padding: "20dp"
                    size_hint_y: None
                    height: "120dp"
                    style: "elevated"
                    md_bg_color: app.theme_cls.primaryColor
                    
                    MDLabel:
                        id: welcome_label
                        text: "Welcome back!"
                        font_style: "Headline"
                        role: "small"
                        theme_text_color: "Custom"
                        text_color: "white"
                        
                    MDLabel:
                        id: date_label
                        text: "Today's Date"
                        font_style: "Body"
                        role: "large"
                        theme_text_color: "Custom"
                        text_color: "white"
                        opacity: 0.9
                
                # Focus Score Card
                MDCard:
                    orientation: "vertical"
                    padding: "20dp"
                    size_hint_y: None
                    height: "180dp"
                    style: "elevated"
                    
                    MDLabel:
                        text: "Today's Focus Score"
                        font_style: "Title"
                        role: "medium"
                        
                    MDBoxLayout:
                        size_hint_y: None
                        height: "80dp"
                        spacing: "20dp"
                        
                        MDLabel:
                            id: focus_score_label
                            text: "0%"
                            font_style: "Display"
                            role: "large"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: app.theme_cls.primaryColor
                            
                        MDBoxLayout:
                            orientation: "vertical"
                            spacing: "4dp"
                            
                            MDLabel:
                                id: focus_rating_label
                                text: "N/A"
                                font_style: "Title"
                                role: "small"
                                
                            MDLabel:
                                id: productive_time_label
                                text: "Productive: 0m"
                                font_style: "Body"
                                role: "medium"
                                theme_text_color: "Secondary"
                                
                            MDLabel:
                                id: distraction_time_label
                                text: "Distracted: 0m"
                                font_style: "Body"
                                role: "medium"
                                theme_text_color: "Secondary"
                
                # Quick Actions
                MDBoxLayout:
                    size_hint_y: None
                    height: "56dp"
                    spacing: "12dp"
                    
                    MDButton:
                        style: "filled"
                        on_release: app.go_to_screen('focus')
                        
                        MDButtonIcon:
                            icon: "timer"
                            
                        MDButtonText:
                            text: "Start Focus"
                            
                    MDButton:
                        style: "outlined"
                        on_release: app.go_to_screen('tasks')
                        
                        MDButtonIcon:
                            icon: "plus"
                            
                        MDButtonText:
                            text: "Add Task"
                            
                # Priority Tasks Card
                MDCard:
                    orientation: "vertical"
                    padding: "16dp"
                    size_hint_y: None
                    height: "300dp"
                    style: "elevated"
                    
                    MDBoxLayout:
                        size_hint_y: None
                        height: "40dp"
                        
                        MDLabel:
                            text: "Priority Tasks"
                            font_style: "Title"
                            role: "medium"
                            
                        MDButton:
                            style: "text"
                            on_release: app.go_to_screen('tasks')
                            
                            MDButtonText:
                                text: "View All"
                                
                    ScrollView:
                        MDList:
                            id: tasks_list
                            
                # Stats Row
                MDBoxLayout:
                    size_hint_y: None
                    height: "100dp"
                    spacing: "12dp"
                    
                    MDCard:
                        orientation: "vertical"
                        padding: "12dp"
                        style: "elevated"
                        
                        MDLabel:
                            id: tasks_completed_label
                            text: "0"
                            font_style: "Headline"
                            role: "large"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: app.theme_cls.primaryColor
                            
                        MDLabel:
                            text: "Tasks Done"
                            font_style: "Body"
                            role: "small"
                            halign: "center"
                            theme_text_color: "Secondary"
                            
                    MDCard:
                        orientation: "vertical"
                        padding: "12dp"
                        style: "elevated"
                        
                        MDLabel:
                            id: sessions_label
                            text: "0"
                            font_style: "Headline"
                            role: "large"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: app.theme_cls.primaryColor
                            
                        MDLabel:
                            text: "Focus Sessions"
                            font_style: "Body"
                            role: "small"
                            halign: "center"
                            theme_text_color: "Secondary"
                            
                    MDCard:
                        orientation: "vertical"
                        padding: "12dp"
                        style: "elevated"
                        
                        MDLabel:
                            id: streak_label
                            text: "0"
                            font_style: "Headline"
                            role: "large"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: app.theme_cls.primaryColor
                            
                        MDLabel:
                            text: "Day Streak"
                            font_style: "Body"
                            role: "small"
                            halign: "center"
                            theme_text_color: "Secondary"
''')


class HomeScreen(MDScreen):
    """Home dashboard with focus score and priority tasks"""
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh all dashboard data"""
        from kivymd.app import MDApp
        from datetime import datetime
        
        app = MDApp.get_running_app()
        
        # Update welcome message
        if app.user:
            name = app.user.get('name', 'User')
            self.ids.welcome_label.text = f"Welcome back, {name}! 👋"
        
        # Update date
        today = datetime.now().strftime("%A, %B %d, %Y")
        self.ids.date_label.text = today
        
        # Get analytics
        self.load_analytics(app)
        
        # Get tasks
        self.load_tasks(app)
        
        # Get streak
        self.load_streak(app)
    
    def load_analytics(self, app):
        """Load daily analytics"""
        result = app.api.get_daily_analytics()
        
        if result.get("success"):
            data = result.get("data", {})
            
            # Update focus score
            score = data.get("focus_score", 0)
            rating = data.get("focus_rating", "N/A")
            self.ids.focus_score_label.text = f"{score}%"
            self.ids.focus_rating_label.text = rating
            
            # Update times
            productive = data.get("productive_time_formatted", "0m")
            distraction = data.get("distraction_time_formatted", "0m")
            self.ids.productive_time_label.text = f"Productive: {productive}"
            self.ids.distraction_time_label.text = f"Distracted: {distraction}"
            
            # Update stats
            self.ids.tasks_completed_label.text = str(data.get("tasks_completed", 0))
            self.ids.sessions_label.text = str(data.get("focus_sessions", 0))
    
    def load_tasks(self, app):
        """Load priority tasks"""
        result = app.api.get_tasks("pending")
        
        # Clear existing tasks
        self.ids.tasks_list.clear_widgets()
        
        if result.get("success"):
            tasks = result.get("data", {}).get("tasks", [])[:3]  # Top 3
            
            for task in tasks:
                urgency = task.get("urgency_level", "MEDIUM")
                icon = "alert-circle" if urgency in ["OVERDUE", "HIGH"] else "checkbox-blank-circle-outline"
                icon_color = task.get("urgency_color", "#FFFFFF")
                
                item = MDListItem(
                    MDListItemLeadingIcon(icon=icon, theme_icon_color="Custom", icon_color=icon_color),
                    MDListItemHeadlineText(text=task.get("title", "Task")),
                    MDListItemSupportingText(text=f"{urgency} • {task.get('days_remaining', 0)} days left")
                )
                self.ids.tasks_list.add_widget(item)
            
            if not tasks:
                item = MDListItem(
                    MDListItemLeadingIcon(icon="check-circle", theme_icon_color="Custom", icon_color="#4CAF50"),
                    MDListItemHeadlineText(text="No pending tasks!"),
                    MDListItemSupportingText(text="Great job! Add new tasks to stay productive.")
                )
                self.ids.tasks_list.add_widget(item)
    
    def load_streak(self, app):
        """Load streak data"""
        result = app.api.get_streak()
        
        if result.get("success"):
            streak = result.get("data", {}).get("streak", 0)
            self.ids.streak_label.text = str(streak)
