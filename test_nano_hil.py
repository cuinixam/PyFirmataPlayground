#!/usr/bin/env python3

from dataclasses import dataclass
from enum import Enum
import logging
import pyfirmata
import time


logging.basicConfig(level=logging.DEBUG)

class RelayID(Enum):
    RELAY1 = 1
    RELAY2 = 2
    
class RelayState(Enum):
    OPEN = 1
    CLOSED = 2,
    UNDEFINED = 13
    

@dataclass()
class Relay:
    control_pin: int
    state_pin: int
    
    

class NanoHil:
    board = None
    relays = {
        RelayID.RELAY1: Relay(6, 2),
        RelayID.RELAY2: Relay(7, 3)
    }
    
    def __init__(self, serial_port: str) -> None:
        self.logger = logging.getLogger(__name__)
        if not self.board:
            self.board = pyfirmata.Arduino(serial_port)
            self.init_board()
            self.start_reading_data_from_board()
            
    def init_board(self):
        for relay_id, relay in self.relays.items():
            input_pin = self.board.digital[relay.control_pin]
            input_pin.mode = pyfirmata.OUTPUT
            output_pin = self.board.digital[relay.state_pin]
            output_pin.mode = pyfirmata.INPUT
            self.close_relay(relay_id)
            
    def start_reading_data_from_board(self):
        pyfirmata.util.Iterator(self.board).start()

    def open_relay(self, relay: RelayID):
        self.logger.info(f"Open relay {relay}")
        self._set_relay_state(relay, 1)
    
    def close_relay(self, relay: RelayID):
        self.logger.info(f"Close relay {relay}")
        self._set_relay_state(relay, 0)
        
    def read_relay_state(self, relay: RelayID) -> RelayState:
        pin = self._get_relay_state_pin(relay)
        state = pin.read()
        self.logger.info(f"Pin value is {state}")
        return RelayState.OPEN if state else RelayState.CLOSED

    def _set_relay_state(self, relay: RelayID, state: int):
        self._get_relay_control_pin(relay).write(state)
        
    def _get_relay_control_pin(self, relay: RelayID) -> pyfirmata.Pin:
        return self.board.digital[self.relays[relay].control_pin]
    
    def _get_relay_state_pin(self, relay: RelayID) -> pyfirmata.Pin:
        return self.board.digital[self.relays[relay].state_pin]

def test_toggle_relays():
    hil = NanoHil('COM3')
    for relay in RelayID:
        toggle_relay(hil, relay)    

def toggle_relay(hil: NanoHil, relay: RelayID):
    hil.open_relay(relay)
    time.sleep(.2)
    assert hil.read_relay_state(relay) == RelayState.OPEN, f"Relay {relay.name} should be OPEN"
    hil.close_relay(relay)
    time.sleep(.2)
    assert hil.read_relay_state(relay) == RelayState.CLOSED, f"Relay {relay.name} should be CLOSED"

if __name__ == "__main__":
    hil = NanoHil('COM3')
    while True:
        toggle_relay(hil, RelayID.RELAY2)
