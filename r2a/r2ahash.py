from math import floor
import time
from player.parser import parse_mpd
from r2a.ir2a import IR2A

class R2AHash(IR2A):
  def __init__(self, id):
    super().__init__(id)
    self.quality_id = []
    self.current_quality_id = 0
    self.timer = {
      'average': 0,
      'start': 0,
      'end': 0,
    }
    self.current_quality = {
      'current': 'H',
      'old': 'H'
    }
    self.hash = {
      'L': 1,
      'M': 0.8,
      'H': 0.3,
    }
  def handle_xml_request(self, msg):
    self.send_down(msg)
  
  def handle_xml_response(self, msg):
    self.quality_id = parse_mpd(msg.get_payload()).get_qi()
    self.current_quality_id = floor((len(self.quality_id) - 1)/2)
    self.send_up(msg)

  def get_quality_id(self):
    print(f'--------> {self.current_quality}, {self.timer}')
    return self.quality_id[self.current_quality_id]

  def get_primary_time(self, time):

    if time <= self.hash['H']:
      return 'H'

    if time >= self.hash['L']:
      return 'L'

    if time > self.hash['H'] and time <= self.hash['M']:
      return 'M'
    if time >= self.hash['M'] and time < self.hash['L']:
      return 'M'
  
  def get_quality_by_time(self, timer):
    current = self.get_primary_time(timer)
    old = self.current_quality.get('old')

    if len(old) == 2:
      if old[1] != current and old[0] != current:
        return old[0]
    elif old != current:
      return old + current

    return current


  def update_quality_id(self):
    quality = self.current_quality.get('current')
    old = self.current_quality.get('old')
    average = self.timer.get('average')
    len_quality = len(quality)
    current = self.current_quality_id
    min = 0
    max = len(self.quality_id) - 1

    if len_quality != 1:
      quality = quality[0]

    if average >= 5:
      self.current_quality_id = min
    
    if quality == 'L':
      if current - 1 >= min:
        self.current_quality_id -= 1

    if quality == 'H':
      if current + 1 <= max:
        self.current_quality_id += 1

  def update_quality(self):
    current_timer = self.timer.get('average')

    current = self.current_quality.get('current')
    new_quality = self.get_quality_by_time(current_timer)

    self.current_quality.update({'old': current})
    self.current_quality.update({'current': new_quality})
      

  def handle_segment_size_request(self, msg):
    self.timer.update({'start': time.perf_counter()})
    msg.add_quality_id(self.get_quality_id())
    self.send_down(msg)

  def handle_segment_size_response(self, msg):
    self.timer.update({'end': time.perf_counter()})
    self.timer.update({'average': (self.timer.get('end') - self.timer.get('start'))})
    self.update_quality()
    self.update_quality_id()
    self.send_up(msg)

  def initialize(self):
    pass

  def finalization(self):
    pass