    def _create_bottom_right(self): #vers 5
        """Create the right buttons with all controls in one line"""
        # Get accent color from theme if available

        self.rightbar = QFrame()
        self.rightbar.setFrameStyle(QFrame.Shape.StyledPanel)
        self.rightbar.setFixedHeight(45)
        #self.rightbar.setStyleSheet("background-color: bg_primary;")
        self.rightbar.setObjectName("rightbar")  # For drag detection

        self.layout = QHBoxLayout(self.rightbar)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # Settings button with icon
        self.properties_btn = QPushButton()
        self.properties_btn.setFont(self.button_font)
        # Bold font
        self.theme_font = QFont(self.button_font)
        self.theme_font.setBold(True)
        self.theme_font.setPointSize(14)
        self.themes_btn.setFont(self.theme_font)

        self.themes_btn.setFixedSize(40, 35)
        self.themes_btn.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                color: color;
                border: 2px solid border;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: bg_primary;
                color: color;
            }
        """)

        # Settings button with icon
        self.launch_btn = QPushButton()
        self.launch_btn.setFont(self.button_font)
        self.launch_btn.setIcon(self.main_window._create_launch_icon())
        self.launch_btn.setText("Launch Game")
        self.launch_btn.setIconSize(QSize(20, 20))
        self.launch_btn.setToolTip("launch Emulator")
        if self.main_window:
            self.launch_btn.clicked.connect(self.main_window._on_launch_game)
        self.layout.addWidget(self.launch_btn)


        self.load_core_btn = QPushButton("Load Core")
        self.load_core_btn.setIcon(self.main_window._create_folder_icon())  # ENABLED
        self.load_core_btn.setIconSize(QSize(20, 20))
        self.load_core_btn.setMinimumHeight(30)
        self.load_core_btn.setToolTip("Browse and load emulator cores")
        if self.main_window:
            self.load_core_btn.clicked.connect(self.main_window._show_load_core)
        button_layout.addWidget(self.load_core_btn)

        # Art manager
        self.gameart_btn = QPushButton("Art Manager")
        self.gameart_btn.setIcon(self.main_window._create_paint_icon())  # ENABLED
        self.gameart_btn.setIconSize(QSize(20, 20))
        self.gameart_btn.setMinimumHeight(30)
        if self.main_window:
            self.gameart_btn.clicked.connect(self.main_window._download_game_artwork)
        button_layout.addWidget(self.gameart_btn)

        button_layout.addStretch()

        # Games manager
        self.manage_btn = QPushButton("Game Manager")
        self.manage_btn.setIcon(self.main_window._create_manage_icon())  # ENABLED
        self.manage_btn.setIconSize(QSize(20, 20))
        self.manage_btn.setMinimumHeight(30)
        if self.main_window:
            self.manage_btn.clicked.connect(self.main_window._show_game_manager)
        button_layout.addWidget(self.manage_btn)

        # Games ports list
        self.ports_btn = QPushButton("Game Ports")
        self.ports_btn.setIcon(self.main_window._create_package_icon())  # ENABLED
        self.ports_btn.setIconSize(QSize(20, 20))
        self.ports_btn.setMinimumHeight(30)
        if self.main_window:
            self.ports_btn.clicked.connect(self.main_window._show_ports_manager)
        button_layout.addWidget(self.ports_btn)

        # Stop button
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setIcon(self.main_window._create_stop_icon())  # ENABLED
        self.stop_btn.setIconSize(QSize(20, 20))
        self.stop_btn.setMinimumHeight(30)
        if self.main_window:
            self.stop_btn.clicked.connect(self.main_window._on_stop_emulation)
        button_layout.addWidget(self.stop_btn)

        main_layout.addWidget(button_frame)

        titlebar = self.titlebar
        return titlebar
