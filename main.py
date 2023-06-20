import MainMenu, StartMenu, GameScreen, EndScreen, Configuration
import Control

states = {'MainMenu': MainMenu.MainMenu(),
          'Configuration': Configuration.Configuration(),
          'StartMenu': StartMenu.StartMenu(),
          'GameScreen': GameScreen.GameScreen(),
          'EndScreen': EndScreen.EndScreen()}

app = Control.Control(states, 'MainMenu')
app.main_game_loop()