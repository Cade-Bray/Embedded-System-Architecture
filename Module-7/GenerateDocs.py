"""
This python file is a script that will execute the diagrams portion of the python-statemachine per their documentation.
Ensure that you've pip installed python-statemachine[diagrams] to execute this file.
"""

from statemachine.contrib.digram import DotGraphMachine
import Thermostat as Thermo

if __name__ == '__main__':
    # Taking the state machine we made
    tsm = Thermo.TemperatureMachine()

    graph = DotGraphMachine(tsm)

    dot = graph()

    print(dot.to_string)

    dot.write_png('StateMachine.png')

