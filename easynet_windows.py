import sys
import os
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolBar, QAction, 
                            QLineEdit, QVBoxLayout, QWidget, QTabWidget, 
                            QFileDialog, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView


class BrowserTab(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def createWindow(self, windowType):
        # Создаем новую вкладку для открытия ссылок в новом окне
        return self.parent.create_new_tab()


class BrowserWindow(QMainWindow):
    def __init__(self, initial_url=None):
        super().__init__()
        self.setWindowTitle("EasyNET - наилегчайший браузер на Python, сделанный благодаря Kolyadual")
        self.setGeometry(100, 100, 1024, 768)
        
        # Создаем виджет вкладок
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        
        # Создаем панель инструментов
        self.setup_toolbar()
        
        # Обработка начального URL
        if initial_url:
            if os.path.isfile(initial_url):
                self.open_local_file(initial_url)
            else:
                if not initial_url.startswith(('http://', 'https://', 'file://')):
                    initial_url = 'https://' + initial_url
                self.create_new_tab(QUrl(initial_url))
        else:
            self.create_new_tab(QUrl("https://kolyadual.github.io/easynet-web/"))
        

    
    def setup_toolbar(self):
        nav_toolbar = QToolBar("Navigation")
        self.addToolBar(nav_toolbar)
        
        # Кнопка "Назад"
        back_btn = QAction("←", self)
        back_btn.setStatusTip("Назад")
        back_btn.triggered.connect(lambda: self.current_browser().back())
        nav_toolbar.addAction(back_btn)
        
        # Кнопка "Вперед"
        forward_btn = QAction("→", self)
        forward_btn.setStatusTip("Вперед")
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        nav_toolbar.addAction(forward_btn)
        
        # Кнопка "Обновить"
        reload_btn = QAction("↻", self)
        reload_btn.setStatusTip("Обновить")
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        nav_toolbar.addAction(reload_btn)
        
        # Кнопка "Домой"
        home_btn = QAction("⌂", self)
        home_btn.setStatusTip("Домой")
        home_btn.triggered.connect(self.navigate_home)
        nav_toolbar.addAction(home_btn)
        
        # Кнопка "Открыть файл"
        open_btn = QAction("📂", self)
        open_btn.setStatusTip("Открыть локальный файл")
        open_btn.triggered.connect(self.open_file_dialog)
        nav_toolbar.addAction(open_btn)
        
        # Кнопка "Новая вкладка"
        new_tab_btn = QAction("➕", self)
        new_tab_btn.setStatusTip("Новая вкладка")
        new_tab_btn.triggered.connect(lambda: self.create_new_tab())
        nav_toolbar.addAction(new_tab_btn)
        
        # Адресная строка
        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        nav_toolbar.addWidget(self.urlbar)
        
        # Обновление URL при изменении
        self.tabs.currentChanged.connect(self.update_urlbar_from_tab)
    
    def create_new_tab_button(self):
        new_tab_btn = QAction("+", self)
        new_tab_btn.setStatusTip("Новая вкладка")
        new_tab_btn.triggered.connect(lambda: self.create_new_tab())
        return new_tab_btn
    
    def create_new_tab(self, url=None):
        # Создаем новую вкладку с браузером
        browser = BrowserTab(self)
        
        if url:
            browser.setUrl(url)
        else:
            browser.setUrl(QUrl("https://google.com"))
        
        # Добавляем вкладку
        index = self.tabs.addTab(browser, "Новая вкладка")
        self.tabs.setCurrentIndex(index)
        
        # Обновляем URL при навигации
        browser.urlChanged.connect(lambda q, browser=browser: self.update_tab_url(q, browser))
        
        # Обновляем заголовок при изменении
        browser.titleChanged.connect(lambda title, browser=browser: self.update_tab_title(title, browser))
        
        return browser
    
    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            QMessageBox.information(self, "Ошибка", "Нельзя закрыть последнюю вкладку")
    
    def current_browser(self):
        return self.tabs.currentWidget()
    
    def navigate_home(self):
        self.current_browser().setUrl(QUrl("https://kolyadual.github.io/dualgamingcentre"))
    
    def navigate_to_url(self):
        url = self.urlbar.text()
        
        # Проверяем, является ли ввод локальным файлом
        if os.path.isfile(url):
            self.open_local_file(url)
            return
        
        # Обрабатываем URL
        if not url.startswith(('http://', 'https://', 'file://')):
            url = 'https://' + url
        
        self.current_browser().setUrl(QUrl(url))
    
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть HTML файл", "", 
            "HTML Files (*.html *.htm);;All Files (*)"
        )
        
        if file_path:
            self.open_local_file(file_path)
    
    def open_local_file(self, file_path):
        # Преобразуем путь в file:// URL
        file_url = QUrl.fromLocalFile(os.path.abspath(file_path))
        self.create_new_tab(file_url)
    
    def update_urlbar_from_tab(self):
        browser = self.current_browser()
        if browser:
            self.urlbar.setText(browser.url().toString())
            self.urlbar.setCursorPosition(0)
    
    def update_tab_url(self, q, browser):
        if browser == self.current_browser():
            self.urlbar.setText(q.toString())
            self.urlbar.setCursorPosition(0)
    
    def update_tab_title(self, title, browser):
        index = self.tabs.indexOf(browser)
        if title == "about:blank":
            title = "Новая вкладка"
        elif len(title) > 15:
            title = title[:15] + "..."
        self.tabs.setTabText(index, title)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Обработка аргументов командной строки
    initial_url = None
    if len(sys.argv) > 1:
        initial_url = sys.argv[1]
    
    window = BrowserWindow(initial_url)
    window.show()
    
    sys.exit(app.exec_())