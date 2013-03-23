#NEAT Composer text version. This version uses OOP to make it cleaner 
#and hopefully make transfering to a GUI easier. Also puts fitness
#functions and other messy stuff in the fitness_func.py file.

import sys
import MultiNEAT as NEAT
#from mingus.midi import fluidsynth  # Commented out until they work on lab machines
#from mingus.midi import MidiFileOut
from mingus.containers.Track import Track
from mingus.containers.Bar import Bar
from mingus.containers.Note import Note
from mingus.core import *
import random
import fitness_func  #contains fitness functions and other useful stuff
from Tkinter import *
import tkSimpleDialog
import tkFileDialog

LENGTH = 12.0 #Global var for song length, must be a multiple of 4 for now
GEN_NUM = 0
#Song class that keeps all the information about the song in one place, including
#the track itself, it's fitness, what generation it belongs to, it's length, etc
params = NEAT.Parameters()
params.PopulationSize = 12

params.DynamicCompatibility = True
params.CompatTreshold = 2.0
params.YoungAgeTreshold = 15
params.SpeciesMaxStagnation = 100
params.OldAgeTreshold = 35
params.MinSpecies = 5
params.MaxSpecies = 25
params.RouletteWheelSelection = False
params.RecurrentProb = 0
params.OverallMutationRate = 0.33

params.MutateWeightsProb = 0.90

params.WeightMutationMaxPower = 5.0
params.WeightReplacementMaxPower = 5.0
params.MutateWeightsSevereProb = 0.5
params.WeightMutationRate = 0.75
params.MaxWeight = 20

params.MutateAddNeuronProb = 0.01
params.MutateAddLinkProb = 0.05
params.MutateRemLinkProb = 0.05

rng = NEAT.RNG()
#rng.TimeSeed()
rng.Seed(0)



genome = NEAT.Genome(0,2,0,7,False,NEAT.ActivationFunction.UNSIGNED_SIGMOID,NEAT.ActivationFunction.UNSIGNED_SIGMOID, 0, params)



class Song:

  song = Track()
  fitness = 0
  gen_num = 0
  leader = False
  length = 0.0
  song_id = 0
  bpm = 150

  def __init__(self, genome, gen_num, song_id, length): #Global var for song length, song_id):
  
    self.genome = genome
    self.gen_num = gen_num 
    self.song_id = song_id
    self.length = length

  def gen_song(self): #Generates the notes by activating the network with various inputs
 		      #representing time and beat of measure from 0-1
    net = NEAT.NeuralNetwork()
    self.genome.BuildPhenotype(net)
    time = 0.0
    beat = 0.25
    track = Track()

    while(time <= 0.999999999):
      net.Input([time, beat])
      net.Activate()
      output = net.Output()[0]*88
      track + fitness_func.note_list[int(output)]
      beat = (beat+0.25)%1
      time = time + (1.0/self.length)
    self.song = track
    return

  def print_song(self): #Prints the song id and the notes (add duration too?)
    str_song = str(self.song_id) + " "
    for x in range(0,(int)(self.length/4)):
      for num in range(0,4): str_song = str_song + str(self.song[x][num][2][0])
    
#    print
    return str_song

  def play_song(self):  #Plays the song at 150 BPM using fluidsynth(make BPM a var later?)
    pass
 #   fluidsynth.play_Track(self.song, 1, 150)
    #return

  def export_song(self, filename):
    pass
   # MidiFileOut.write_Track(filename, self.song, self.bpm, 0)
    #pass
    
#End of Song Class


def evaluate(a_song, fitness_func, genome, *args):      #Takes a song and fitness function, then evaluates
  a_song.fitness = fitness_func(a_song, *args)
  genome.SetFitness(a_song.fitness); 
	 #the song via that fitness function. Also sets the
  return a_song.fitness 				         #song_fitness attribute


def advance_gen(genome_list):  #Advances population to next generation
  global GEN_NUM
  song_list2 = []
  x = 1
  GEN_NUM = GEN_NUM+1
  for genomes in genome_list:
    c = Song(genomes, GEN_NUM, x, LENGTH)
    song_list2.append(c)
    song_list2[x-1].gen_song()
    x = x+1
  return song_list2


def song_clicked(i):
  index = int(listbox.curselection()[0])
  print(song_list[index].print_song())
  song_list[index].play_song()

def print_all():
  for song in song_list:
    print song.print_song() + "\n"  

def in_key_choice():
  global choice
  choice = tkSimpleDialog.askstring("Key Choice", "Enter key you with to restrict to")
  print "In key choice is", choice

def evaluate_pop():
  args = (choice)
  y = 0
  for genomes in genome_list:
    evaluate(song_list[y], fitness_func.functions[func_choice.get()], genomes, *args)
    y = y + 1
  listbox.delete(0, END);
  for song in song_list:
    listbox.insert(END, "Song: "+ str(song.song_id) + "    Fitness:" + str( song.fitness))

def evolve_pop():
  global population
  global song_list
  global genome_list
  population.Epoch()
  genome_list = NEAT.GetGenomeList(population)
  song_list = advance_gen(genome_list)
  listbox.delete(0, END)
  for song in song_list:
    listbox.insert(END, "Song: "+ str(song.song_id) + "    Fitness:" + str( song.fitness))

def export():
  filename = tkFileDialog.asksaveasfilename(parent = root)
  song = listbox.index(ACTIVE)
  print filename, song
  song_list[song].export_song(filename)
  
  
def main():
  #creates default NEAT Genome
  
  
  population = NEAT.Population(genome, params, True, 1.0)
  genome_list = NEAT.GetGenomeList(population)
  song_list = advance_gen(genome_list)

#Main program loop
  while(1):
    choice = raw_input("Choose one of the following\n1) Print population\n2) Eval pop with fitness function\n3) Manually assign fitness\n4) Print fitness of POP\n5) Play a song\n6) Advance to next Generation\n7) Export song to midi file\n8) Exit\n")
  
    if(choice == "1"): #Goes through and prints all songs
      for song in song_list:
        song.print_song()

    elif(choice == "2"): #User picks a fitness function and all songs are evaluated 
  		     #using that fitness function. Can happen for many generations
      func_choice = raw_input("Select fitness function: diatonic, or in_key\n")
      args = ()
      if(func_choice == "in_key"):
        arg1 = raw_input("What key would you like to use? A, B, etc...\n")
	args = (arg1)

      num_repeats = raw_input("How many gens would you like to run?\n")
      for x in range(0, int(num_repeats)):
	y = 0
        fitness_sum = 0
        for genomes in genome_list:
          evaluate(song_list[y], (fitness_func.functions[func_choice]),genomes, *args )
          fitness_sum += song_list[y].fitness
	  y = y+1
	print "Gen", GEN_NUM, "has average fitness of:",(fitness_sum / y)
	population.Epoch()
	genome_list = NEAT.GetGenomeList(population)
	song_list = advance_gen(genome_list)
    
      y = 0
      for genomes in genome_list:
        evaluate(song_list[y], (fitness_func.functions[func_choice]),genomes, *args )
        y = y + 1



    elif(choice == "3"): #Pick a song out of the population and change it's fitness
      song_choice = raw_input("Which song's fitness would you like to change?\n")
      new_fit = raw_input("Enter new fitness\n")
      old_fit = song_list[(int)(song_choice)-1].fitness
      song_list[(int)(song_choice)-1].fitness = new_fit
      print "Song", song_choice, "fitness changed from", old_fit, "to", new_fit, "\n"

    elif(choice == "4"):
      for song in song_list:
        print "Song", song.song_id , "has fitness", song.fitness

    elif(choice == "5"): #Gets user choice of song and plays it
      song_choice = (int)(raw_input("Which song would you like to play?\n"))
      song_list[song_choice-1].play_song()
  
    elif(choice == "6"): #Advances to next generation and gets new population/songs
      y = 0
      for genomes in genome_list: #Shouldn't be necessary, but just in case
	genomes.SetFitness(song_list[y].fitness)
      population.Epoch()
      genome_list = NEAT.GetGenomeList(population)
      song_list = advance_gen(genome_list)
      

    elif(choice == "7"): #Exports to midi file
      song_choice = (int)(raw_input("Which song would you like to export?\n"))
      file_name = raw_input("Enter filename of midi file you want to create?\n")
      song_list[song_choice-1].export_song(file_name)

    elif(choice == "8"): #exits program
      sys.exit("Program exited")



#main()

choice = "C"


population = NEAT.Population(genome, params, True, 1.0)
genome_list = NEAT.GetGenomeList(population)
song_list = advance_gen(genome_list)



root = Tk()
frame = Frame(root)
frame.grid(row=0, column=0)

framelistbox = Frame(root)
framelistbox.grid(row = 0, column = 2)

func_choice = StringVar()
func_choice.set("DEFAULT")

evaluateButton = Button(frame, text = "Evaluate population", command = evaluate_pop)
evaluateButton.grid(row = 2, column = 0)

evolveButton = Button(frame, text = "Evolve population", command = evolve_pop)
evolveButton.grid(row = 3, column = 0)

menu = Menu(root)
filemenu = Menu(menu)
menu.add_cascade(label="File", menu = filemenu)
filemenu.add_command(label = "Export Song", command = export)

viewmenu = Menu(menu)
menu.add_cascade(label = "View", menu = viewmenu)
viewmenu.add_command(label = "Print all", command = print_all)

root.config(menu = menu)

yscroll = Scrollbar(framelistbox, relief = 'raised')
yscroll.grid(row=0, column=1)


listbox = Listbox(framelistbox, yscrollcommand = yscroll.set, width = 20, height = 8)
for song in song_list:
  listbox.insert(END, "Song: "+ str(song.song_id) + "    Fitness:" + str( song.fitness))
listbox.grid(row = 0, column = 0)
yscroll.config(command = listbox.yview)
listbox.bind('<<ListboxSelect>>', song_clicked)

fitnesslabel = Label(frame, text = "Fitness Functions")
fitnesslabel.grid(row = 0, column = 0)

in_key_label = Radiobutton(frame, text = "In Key", variable = func_choice, value = "in_key", command = in_key_choice)
in_key_label.grid(row = 1, column = 0)

diatonic_label = Radiobutton(frame, text = "Diatonic", variable = func_choice, value = "diatonic")
diatonic_label.grid(row = 1, column = 1)



root.mainloop()
