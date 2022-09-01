from math import floor
import time
from player.parser import parse_mpd
from r2a.ir2a import IR2A
from dotenv import dotenv_values


ENV = dotenv_values('.env')
MAX_LENGTH = int(ENV['MAX_LEN'])

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
      'M': 0.3,
      'H': 0.2,
    }
  def handle_xml_request(self, msg):
    self.send_down(msg)
  
  def handle_xml_response(self, msg):
    self.quality_id = parse_mpd(msg.get_payload()).get_qi()
    self.current_quality_id = len(self.quality_id) - 1
    self.send_up(msg)

  def get_quality_id(self):
    return self.quality_id[self.current_quality_id]
  
  def get_quality_by_time(self, timer):
    value = 'L'
    if timer >= self.hash['L']:
      value = 'L'
    elif timer <= self.hash['H']:
      value = 'H'
    elif timer > self.hash['H'] and timer <= self.hash['M']:
      value = 'M'
    elif timer >= self.hash['M'] and timer < self.hash['L']:
      value = 'M'

    old = self.current_quality.get('old')

    if value == 'H' and old == 'M':
      return 'MH'
    if value == 'H' and old == 'L':
      return 'LH'
    if value == 'M' and old == 'H':
      return 'HM'
    if value == 'M' and old == 'L':
      return 'LM'
    if value == 'L' and old == 'H':
      return 'HL'
    if value == 'L' and old == 'M':
      return 'ML'
    if value == old:
      return value

    if value == 'H' and old == 'HM':
      return 'H'
    if value == 'H' and old == 'HL':
      return 'H'
    if value == 'H' and old == 'MH':
      return 'H'
    if value == 'H' and old == 'ML':
      return 'M'
    if value == 'H' and old == 'LH':
      return 'H'
    if value == 'H' and old == 'LM':
      return 'L'
    
    if value == 'M' and old == 'HM':
      return 'M'
    if value == 'M' and old == 'HL':
      return 'H'
    if value == 'M' and old == 'MH':
      return 'M'
    if value == 'M' and old == 'ML':
      return 'M'
    if value == 'M' and old == 'LH':
      return 'L'
    if value == 'M' and old == 'LM':
      return 'M'
    
    if value == 'L' and old == 'HM':
      return 'H'
    if value == 'L' and old == 'HL':
      return 'H'
    if value == 'L' and old == 'MH':
      return 'M'
    if value == 'L' and old == 'ML':
      return 'L'
    if value == 'L' and old == 'LH':
      return 'L'
    if value == 'L' and old == 'LM':
      return 'L'


  def update_quality_id(self):
    quality = self.current_quality.get('current')
    len_quality = len(quality)
    current = self.current_quality_id
    min = 0
    max = len(self.quality_id) - 1
    mid = floor(max/2)

    if len_quality != 1:
      quality = quality[0]
    
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
    self.hash.clear()
    pass