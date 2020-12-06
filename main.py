# pylint: disable=unused-variable

import tkinter
import time
import random
import math
import numpy as np
import pickle

default_game_canvas_width=1200
default_game_canvas_height=800
default_stats_canvas_height=200
default_free_border=50  

class Game: 
  def __init__(self, *args):    

    #Settings
    self.game_canvas_width=default_game_canvas_width
    self.game_canvas_height=default_game_canvas_height
    self.stats_canvas_height=default_stats_canvas_height
    self.free_border=default_free_border 
    self.animation = True
    self.animation_refresh_seconds = 1/60 #60fps
    self.population_size = 4
    self.uniform = True
    self.new_generation_age_seconds = 17
    self.new_generation_age_ticks = 1000
    self.global_timer_ticks = 0
    self.global_timer_seconds = 0    
    self.current_generation_age_ticks = 0
    self.current_generation_age_seconds = 0
    self.current_generation = 1    
    self.grid = 50
    self.debug = False
    self.is_paused = False

    # Initial game setup
    self.window = tkinter.Tk()
    self.window.title("Battle Balls")
    self.window.geometry(f'{self.game_canvas_width}x{self.game_canvas_height+self.stats_canvas_height}')

    self.game_canvas = tkinter.Canvas(self.window)
    self.game_canvas.configure(bg="white", height = self.game_canvas_height, width = self.game_canvas_width, borderwidth=0, highlightthickness=0)
    self.game_canvas.pack()

    self.stats_canvas = tkinter.Canvas(self.window)
    self.stats_canvas.configure(bg="white", height = self.stats_canvas_height, width = self.game_canvas_width)
    self.stats_canvas.pack()

    self.population = self.populate()

  def get_uniform_coordinates(self):

      ucoord = []

      if self.uniform == True:

        start_x = self.free_border
        end_x = self.game_canvas_width - self.free_border        
        start_y = self.free_border
        end_y = self.game_canvas_height - self.free_border     
        space_for_one_x = int ((end_x - start_x) / math.sqrt(self.population_size))
        space_for_one_y = int ((end_y - start_y) / math.sqrt(self.population_size))

        for lx in range(start_x + space_for_one_x // 2, end_x, space_for_one_x):
          for ly in range(start_y + space_for_one_y // 2, end_y, space_for_one_y):
            ucoord.append({"x": lx + random.randrange(-10, 10), "y": ly + random.randrange(-10, 10)})

      else:

        for xy in range(0, self.population_size):
            ucoord.append({"x": random.randrange(self.free_border, self.game_canvas_width - self.free_border), "y": random.randrange(self.free_border, self.game_canvas_height - self.free_border)})

      return ucoord

  def populate(self):

      pop = []

      uniform_coordinates = self.get_uniform_coordinates()

      for i in range(0, self.population_size):
        pop.append(NewEntity(uniform_coordinates[i]["x"], uniform_coordinates[i]["y"], self))
      
      return pop

  def tpopulate(self): #test population - manual

      pop = []

      ball = NewEntity(400, 400, self)
      ball.set_speed(0)
      ball.set_ai(False)           
      ball.set_size(50)
      ball.set_head_size(120)           
      ball.set_facing_degrees(180)
      ball.set_sensitivity(2)

      pop.append(ball)

      ball = NewEntity(510, 600, self)
      ball.set_speed(3)
      ball.set_size(50)
      ball.set_ai(False)            
      ball.set_head_size(120)           
      ball.set_facing_degrees(180)
      ball.set_sensitivity(10)

      pop.append(ball)

      # ball = NewEntity(400, 650, self)
      # ball.set_speed(1)
      # ball.set_size(50)
      # ball.set_ai(False)              
      # ball.set_head_size(190)      
      # ball.set_facing_degrees(15)
      # ball.set_sensitivity(3)
    
      # pop.append(ball)

      return pop

  def calculate(self):

      for ball in self.population:
        if ball.get_is_alive():  

          if self.is_paused == False:
            # Calculate movement
            ball.set_x(ball.get_x() + ball.get_speed() * math.sin(ball.get_facing()))
            ball.set_y(ball.get_y() + ball.get_speed() * math.cos(ball.get_facing()))          

          # don't allow moving into other balls

          # Update stars
          current_distance_from_origin = math.sqrt((ball.get_stat("original_x") - ball.get_x())**2 + (ball.get_stat("original_y") - ball.get_y())**2)

          if current_distance_from_origin > ball.get_stat("max_distance_from_origin"):
            ball.set_stat("max_distance_from_origin", current_distance_from_origin)
          ball.set_stat("traveled", ball.get_stat("traveled") + ball.get_speed())

          # Set sensor initial before checking
          ball.set_sensor_input(0)

          # Detect borders and border hits
          if ball.get_x() >= self.game_canvas_width - ball.get_sensor_size():
            ball.set_sensor_input_degrees(90)
          if ball.get_x() <= ball.get_sensor_size():      
            ball.set_sensor_input_degrees(270)
          if ball.get_y() >= self.game_canvas_height - ball.get_sensor_size():
            ball.set_sensor_input_degrees(360)
          if ball.get_y() < ball.get_sensor_size():
            ball.set_sensor_input_degrees(180)
          if ball.get_x() > self.game_canvas_width - ball.get_size() or ball.get_x() < ball.get_size() or ball.get_y() > self.game_canvas_height - ball.get_size() or ball.get_y() < ball.get_size():
            ball.kill()

          # Detect other ball hits
          for other_ball in self.population:
            
            distance_between_balls = math.sqrt((ball.get_x() - other_ball.get_x())**2 + (ball.get_y() - other_ball.get_y())**2)

            if other_ball != ball and distance_between_balls <= ball.get_sensor_size() + other_ball.get_size():

              dx = abs(other_ball.get_x() - ball.get_x())
              dy = abs(other_ball.get_y() - ball.get_y())
              dd = (math.sqrt( dx**2 + dy**2 ))

              if dd != 0:
                if ball.get_y() < other_ball.get_y():        
                  if ball.get_x() < other_ball.get_x():                                 
                    ball.set_sensor_input(+math.acos(dy / dd))
                  else:
                    ball.set_sensor_input(-math.acos(dy / dd))
                else:           
                  if ball.get_x() < other_ball.get_x():                      
                    ball.set_sensor_input(math.pi - math.acos(dy / dd))
                  else:
                    ball.set_sensor_input(math.pi + math.acos(dy / dd))                  

            if other_ball != ball and distance_between_balls <= ball.get_size() + other_ball.get_size():     
              if (ball.get_sensor_input_degrees() <= ball.get_facing_degrees() - ball.get_head_size()/2 or
                  ball.get_sensor_input_degrees() >= ball.get_facing_degrees() + ball.get_head_size()/2):
                    ball.kill()                         

          if self.is_paused == False and ball.get_speed() != 0 and ball.get_ai() == True:
            # Fire Neurons to get new "facing" value
            ball.set_facing(ball.fire_neurons(self))

  def animate(self, active):
      if active:
        self.animation = True
        self.game_canvas.delete("all")

#Draw grid 
      if self.grid != False:
        grid_line_width = 2
        for x in range(0, int(self.game_canvas_width/self.grid)):
          self.game_canvas.create_line(x*self.grid, 0, x*self.grid, self.game_canvas_height, width=grid_line_width)
          self.game_canvas.create_line(0, self.game_canvas_height-x*self.grid, self.game_canvas_width, self.game_canvas_height-x*self.grid, width=grid_line_width)
          if grid_line_width == 2:
            grid_line_width = 1
          else:
            grid_line_width = 2

        for ball in self.population:
          self.game_canvas.create_oval(ball.get_rx() - ball.get_size(),
                                      ball.get_ry() - ball.get_size(),
                                      ball.get_rx() + ball.get_size(),
                                      ball.get_ry() + ball.get_size(),
                                      fill=ball.get_color())

          #debugging
          if self.debug == True:
            self.game_canvas.create_text(ball.get_rx(), ball.get_ry()-20, fill = "blue", text="x:"+str(int(ball.get_stat("original_x"))), font=("Purisa", 8, "bold"))
            self.game_canvas.create_text(ball.get_rx(), ball.get_ry()-10, fill = "orange", text="y:"+str(int(ball.get_stat("original_y"))), font=("Purisa", 8, "bold"))
            self.game_canvas.create_text(ball.get_rx(), ball.get_ry(), fill = "black", text="f:"+str(math.degrees(ball.get_facing())), font=("Purisa", 8, "bold"))
            self.game_canvas.create_text(ball.get_rx(), ball.get_ry()+10, fill = "magenta", text="i:"+str(round(ball.get_sensor_input(), 2)), font=("Purisa", 8, "bold"))
            self.game_canvas.create_text(ball.get_rx(), ball.get_ry()+20, fill = "brown", text="s:"+str(ball.get_speed()), font=("Purisa", 8, "bold"))

          self.game_canvas.create_oval(ball.get_rx() - ball.get_sensor_size(),
                                      ball.get_ry() - ball.get_sensor_size(),
                                      ball.get_rx() + ball.get_sensor_size(),
                                      ball.get_ry() + ball.get_sensor_size(),
                                      width = 1, dash=(3,5))

          if ball.get_is_alive() == True and ball.get_sensor_input() != 0:

            self.game_canvas.create_line(ball.get_rx(), 
                                        ball.get_ry(), 
                                        ball.get_rx() + (ball.get_sensor_size()) * math.sin(ball.get_sensor_input()), 
                                        ball.get_ry() - (ball.get_sensor_size()) * math.cos(ball.get_sensor_input()),
                                        width=4, dash=(3,3), fill="blue")

          self.game_canvas.create_arc(ball.get_rx() - ball.get_size(),
                                      ball.get_ry() - ball.get_size(),
                                      ball.get_rx() + ball.get_size(),
                                      ball.get_ry() + ball.get_size(),  
                                      start=-ball.get_facing_degrees()+90-ball.get_head_size()/2,  extent=ball.get_head_size(), fill="black")

        time.sleep(self.animation_refresh_seconds)
      else:
        self.animation = False

  def calculate_next_gen(self):
      return
    # # Select 4 potential parents from based on is_alive and traveled 
    # self.population.sort(key=lambda x: (x.is_alive, x.stats["distance_from_origin"]), reverse=True)
    # best_parents = self.population[0:4]
    # self.current_generation = self.current_generation + 1

    # # Crossover 
    # new_populaiton = self.populate()

    # for child in new_populaiton[:len(new_populaiton)//2:2]:
    #   parents = random.sample(set(best_parents), 2)

    #   child.features["size"] = parents[random.randrange(0, 1)].features["size"]
    #   child.features["speed"] = parents[random.randrange(0, 1)].features["speed"]
    #   child.features["sensitivity"] = parents[random.randrange(0, 1)].features["sensitivity"]

    #   crossover_point = random.randrange(1, 19)
    #   genome_slice1 = parents[0].genome[:crossover_point]
    #   genome_slice2 = parents[1].genome[crossover_point:]
    #   child.genome = np.concatenate((genome_slice1, genome_slice2))

    #   child.features["size"]  = child.features["size"] * ( 0.90 + (random.random() * 0.2) )
    #   child.features["speed"] = child.features["speed"] * ( 0.90 + (random.random() * 0.2) )
    #   child.features["sensitivity"] = child.features["sensitivity"] * ( 0.90 + (random.random() * 0.2) )

    #   for i in range(random.randrange(1, 5)):
    #     swap_random(child.genome)

    # return new_populaiton

class NewEntity:
    def __init__(self, lx, ly, game):
      self.__is_alive = True
      self.__x = 0
      self.__y = 0
      self.__rx = 0
      self.__ry = 0   
      self.__ai = True   
      self.__size = random.random() * 40 + 10
      self.__head_size = 90 + random.random()*90     
      self.__speed = random.random() * 5
      self.__sensitivity = 1 + random.random() * 20
      self.__color = "green"
      self.__facing = random.random() * math.tau
      self.__facing_degrees = math.degrees(self.__facing)
      self.__sensor_input = False
      self.__sensor_input_degrees = False     
      self.__genome = np.array([random.random(), random.random(), random.random(), random.random(),  #Hidden layer weights
                                random.random(), random.random(), random.random(), random.random(),  #Hidden layer weights
                                random.random(), random.random(), random.random(), random.random(),  #Hidden layer weights
                                random.random(), random.random(), random.random(), random.random(),  #Hidden layer weights                              
                                random.random(), random.random(), random.random(), random.random()]) #Output layer weights 
      self.__stats = {"traveled": 0, "age": 0, "generation": game.current_generation, "original_x": 0, "original_y": 0, "max_distance_from_origin": 0}

      #constructor
      self.set_x(lx)
      self.set_y(ly)
      self.set_stat("original_x", self.get_x())
      self.set_stat("original_y", self.get_y())

    def get_is_alive(self):
      return self.__is_alive
    def set_is_alive(self, is_alive):
      self.__is_alive = is_alive

    def get_x(self):
      return self.__x
    def set_x(self, x):
      self.__x = x
      self.__rx = x

    def get_y(self):
      return self.__y
    def set_y(self, y):
      self.__y = y
      self.__ry = default_game_canvas_height - y

    def get_rx(self):
      return self.__rx
    def set_rx(self, rx):
      self.__rx = rx
      self.__x = rx

    def get_ry(self):
      return self.__ry
    def set_ry(self, ry):
      self.ry = ry
      self.y = default_game_canvas_height - ry

    def get_ai(self):
      return self.__ai
    def set_ai(self, ai):
      self.__ai = ai

    def get_size(self):
      return self.__size
    def set_size(self, size):
      self.__size = size

    def get_head_size(self):
      return self.__head_size
    def set_head_size(self, head_size):
      self.__head_size = head_size

    def get_speed(self):
      return self.__speed
    def set_speed(self, speed):
      self.__speed = speed

    def get_sensitivity(self):
      return self.__sensitivity
    def set_sensitivity(self, sensitivity):
      self.__sensitivity = sensitivity

    def get_color(self):
      return self.__color
    def set_color(self, color):
      self.__color = color

    def get_facing(self):
      return self.__facing
    def set_facing(self, facing):
      self.__facing = facing
      self.__facing_degrees = math.degrees(facing)

    def get_facing_degrees(self):
      return self.__facing_degrees
    def set_facing_degrees(self, facing_degrees):
      self.__facing_degrees = facing_degrees
      self.__facing = math.radians(facing_degrees)

    def get_sensor_input(self):
      return self.__sensor_input
    def set_sensor_input(self, sensor_input):
      self.__sensor_input = sensor_input
      self.__sensor_input_degrees = math.degrees(sensor_input)

    def get_sensor_input_degrees(self):
      return self.__sensor_input_degrees
    def set_sensor_input_degrees(self, sensor_input_degrees):
      self.__sensor_input_degrees = sensor_input_degrees
      self.__sensor_input = math.radians(sensor_input_degrees)

    def get_genome(self):
      return self.__genome
    def set_genome(self, genome):
      self.__genome = genome

    def get_stat(self, stat):
      return self.__stats[stat]
    def set_stat(self, stat, value):
      self.__stats[stat] = value

    def get_sensor_size(self):
      return self.get_size() * self.get_sensitivity()

    def kill(self):
          self.set_is_alive(False)
          self.set_color("red")
          self.set_sensor_input(False)

    def hit(self, other):
      if other == self:
        return False
      elif math.sqrt( (self.get_x() - other.get_x())**2 + (self.get_y() - other.get_y())**2 ) <= self.get_size() + other.get_size():
        return True        
      else:
        return False          

        # NN design 3-4-1
    def fire_neurons(self, game):

        output_array = []

        # Get input values and scale to 0-1
        input_data = np.array([scale_to_0_to_1(self.get_x(), 1, game.game_canvas_width),           
                              scale_to_0_to_1(self.get_y(), 1, game.game_canvas_height), 
                              self.get_sensor_input()])

        # Define weights of hidden layer
        hidden_weights = np.array([self.get_genome()[0:4], 
                                  self.get_genome()[4:8],
                                  self.get_genome()[8:12]])
        
        # Define weights of output layer
        output_weights = np.array(self.get_genome()[12:16])

        # Apply hidden weights
        hidden_output = np.dot(input_data, hidden_weights) + 1 #bias

        # hidden_output = sigmoid(hidden_output)

        # Apply output weights
        output_data = np.dot(hidden_output, output_weights)

        # output_data = sigmoid(output_data)

        output_array.append(output_data)

        return ( output_data )

#  Scale down to 0-1
def scale_to_0_to_1(x, in_min, in_max):
    return (x - in_min) / (in_max - in_min)

#  Scale up from 0-1
def scale_from_0_to_1(x, out_min, out_max):
    return out_min + (out_max - out_min) * x

def swap_random(array):
      idx = range(len(array))
      i1, i2 = random.sample(idx, 2)
      array[i1], array[i2] = array[i2], array[i1]

def sigmoid(x):
    return 1 / (1 + np.exp(-x) )

all_games = [Game()]

for Game in all_games:

# Run Game

    # Load population   

    # with open('pop_save.pickle', 'rb') as handle:
    #     Game.population = pickle.load(handle)

    while True:

      Game.calculate()
      Game.animate(True)      
      if Game.animation == True:
        Game.window.update()

      Game.global_timer_seconds = Game.global_timer_seconds + Game.animation_refresh_seconds
      Game.current_generation_age_seconds = Game.current_generation_age_seconds + Game.animation_refresh_seconds
      Game.global_timer_ticks = Game.global_timer_ticks + 1
      Game.current_generation_age_ticks = Game.current_generation_age_ticks + 1

      if (Game.current_generation_age_seconds >= Game.new_generation_age_seconds and Game.animation == True) or (Game.current_generation_age_ticks >= Game.new_generation_age_ticks and Game.animation == False):
          Game.stats_canvas.delete("all")
          # Game.population = Game.calculate_next_gen()
          Game.current_generation_age_ticks = 0
          Game.current_generation_age_seconds = 0

#       if Game.current_generation >= 1000:
# #Use dumps to convert the object to a serialized string

#         with open('pop_save.pickle', 'wb') as handle:
#             pickle.dump(Game.population, handle, protocol=pickle.HIGHEST_PROTOCOL)
#         exit()



