import sys
import io
import folium
import pandas as pd
import requests
import os
import base64
#The QApplication class manages the GUI application’s control flow and main settings.
#The QWidget class is the base class of all user interface objects.
#QHBoxLayout	Linear horizontal layout
#QVBoxLayout	Linear vertical layout
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QMainWindow, QProgressBar, QLabel, QGridLayout
#QtWebEngineWidgets : The framework provides the ability to embed web content in applications and is based on the Chrome browser
#The QWebEngineView class provides a widget that is used to view and edit web documents.
from PyQt5.QtWebEngineWidgets import QWebEngineView
#the primary elements for creating user interfaces in Qt.(get the scrren size) 
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5 import QtGui


def getWeather(city):
    # - get a response from the weather API for the give city
    response = requests.get("https://api.openweathermap.org/data/2.5/weather?q="+city+",gr&APPID=4103d6432a09566f7281c76dc7579f3a")
    response_code = response.status_code
    response_dict = response.json()

    # - get the info we want from the response of the weather api
    if response_code == 200 and response_dict:
        city = response_dict['name']
        weather_icon_path = os.path.join(os.path.join(os.getcwd(), 'icons'), response_dict['weather'][0]['icon']+'@2x.png')
        weather_main_description = response_dict['weather'][0]['description'].title()
        temperature_kelvin = response_dict['main']['temp']
        temperature_celsius = "%d° C" % (temperature_kelvin - 273.15)
        return {'icon':weather_icon_path, 'weather':weather_main_description, 'temperature':temperature_celsius}

    return None

class WeatherApp(QWidget):
    def __init__(self, mainWindow):
        super().__init__()
        self.mainWindow = mainWindow
        self.setWindowTitle('Weather Report')
        #Get current screen size
        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        self.window_width, self.window_height = sizeObject.width(), sizeObject.height()
        self.resize(self.window_width, self.window_height)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # - create the map based on cities from csv file
        # - get current directory
        path = os.getcwd()
        weather_locations = pd.read_csv(os.path.join(os.path.join(path, 'data'), 'greek_towns.csv'))
        weather_locations = weather_locations[["Latitude", "Longitude", "Name"]]
        map_osm = folium.Map(location=[weather_locations.Latitude.mean(), weather_locations.Longitude.mean()], zoom_start=7, control_scale=True)

        # - add to map the markers
        for index, location_info in weather_locations.iterrows():
            ret = getWeather(location_info['Name'])
            if not ret:
                continue

            html = '<figure>'
            html += '<h2 style="font-family:Helvetica">{}</h2>'.format(location_info['Name'])
            # open binary file (the image) for reading (open(image, 'rb') and use base64.b64encode to get binary data
            # into ASCII characters and embody it into the html
            encoded = base64.b64encode(open(ret['icon'], 'rb').read()).decode('UTF-8')
            html += '<img src="data:image/jpeg;base64,{}">'.format(encoded)
            html += '<p  style="font-size:26px; font-family:Helvetica"><b>{}</b></p>'.format(ret['temperature'])
            html += '<p  style="font-size:14px; font-family:Helvetica">{}</p></figure>'.format(ret['weather'])
            
            iframe = folium.IFrame(html, width=250, height=300)

            popup = folium.Popup(iframe, max_width=400)
            folium.Marker([location_info["Latitude"], location_info["Longitude"]], popup=popup, icon=folium.Icon(color = 'gray')).add_to(map_osm)

        #convert map to bytes and save it ot data object
        data = io.BytesIO()
        map_osm.save(data, close_file=False)

        webView = QWebEngineView()
        #convert data to html
        webView.setHtml(data.getvalue().decode())
        #add web object to layout
        layout.addWidget(webView)

    # on close of window with map show again the main window because it is hidden
    def closeEvent(self, event):
        self.mainWindow.show()
        event.accept()

# this is the main window of the program        
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Weather Report")

        # add a gridlayout so that to place the label and buttons in particular location
        grid = QGridLayout()

        # gridlayout is not placed in a QMainWindow but in a central widget of the QMainWindow
        widget = QWidget()
        widget.setLayout(grid)
        self.setCentralWidget(widget)

        # create and place label and buttons
        label = QLabel("Get a city weather report based on map of Greece")
        grid.addWidget(label, 0, 0, 1, 2)
        pushButtonShowMap = QPushButton("Show map")
        grid.addWidget(pushButtonShowMap, 1, 0)
        pushButtonShowMap.move(10, 10)
        pushButtonExit = QPushButton("Exit")
        grid.addWidget(pushButtonExit, 1, 1)
        pushButtonExit.move(150, 10)

        # set a fixed size for the main window
        self.setFixedSize(QSize(320, 120))

        # on push of button Show Map the window of the map will be launched
        # on push of button Exit we exit the program
        pushButtonShowMap.clicked.connect(self.window2)
        pushButtonExit.clicked.connect(self.exit)

    def window2(self):
        # when launching the map window, put a cursor wait while waiting
        # also hide the main window
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.w = WeatherApp(self)
        self.w.show()
        QApplication.restoreOverrideCursor()
        self.hide()

    def exit(self):
        sys.exit(app.exec_())

        
if __name__ == '__main__':
    # the first element of the array sys.argv() is the name of the program itself.
    app =QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    app.exec()
    
