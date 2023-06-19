import MainMenu, StartMenu, GameScreen, EndScreen
import Control

states = {'MainMenu': MainMenu.MainMenu(),
          'StartMenu': StartMenu.StartMenu(),
          'GameScreen': GameScreen.GameScreen(),
          'EndScreen': EndScreen.EndScreen()}

app = Control.Control(states, 'MainMenu')
app.main_game_loop()