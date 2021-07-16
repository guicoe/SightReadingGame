import ui
import random
import time
import threading


class MyUI (ui.View):
	
	
	def __init__(self, w, h):
		self.width = w
		self.height = h
		self.start = 5
		self.end = -1.5
		self.notes = []
		self.best = 0
		
		self.ongoing = False
		self.survival = False
		
		self.scoreboard = ui.Label()
		self.scoreboard.text = "Mode: Blitz  |  Timer: 60s"
		self.instructions = ui.Label()
		self.instructions.text = "Press [ENTER] to start."
		for sgn, field in enumerate([self.instructions, self.scoreboard]):
			field.width = self.width
			field.height = 200
			field.center = (self.width/2, self.height/2 + (-1)**sgn*400)
			field.alignment = ui.ALIGN_CENTER
			field.font = ("<system>", 40)
			self.add_subview(field)
		
		self.timer = 1.5 if self.survival else 60
		
		
	def get_key_commands(self):
		
		# Notes
		s = [{"input": c} for c in "CDEFGAB"]
		
		# Controls
		s.extend([
			{"input": "Q", "title": "End Game"}, 
			{"input": "M", "modifiers": "cmd", "title": "Switch Modes"}, 
			{"input": "up", "modifiers": "cmd", "title": "Increase Timer"}, 
			{"input": "down", "modifiers": "cmd", "title": "Decrease Timer"},
			{"input": "\r"}
		])
		
		return s
		
		
	def key_command(self, sender):
		if sender["input"] == "\r":
			if not self.ongoing:
				self.play()
		elif sender["input"] == "Q":
			if self.ongoing:
				self.game.cancel()
				self.gameover()
		elif sender["input"] == "M":
			if not self.ongoing:
				self.survival = not self.survival
				mode = "Survival" if self.survival else "Blitz"
				self.timer = 1.5 if self.survival else 60
				self.scoreboard.text = "Mode: {}  |  Timer: {}s".format(mode, self.timer)
		elif sender["input"] == "up":
			if not self.ongoing:
				if self.survival:
					mode = "Survival"
					self.timer += 0.5
				else:
					mode = "Blitz"
					self.timer += 5
				self.scoreboard.text = "Mode: {}  |  Timer: {}s".format(mode, self.timer)
		elif sender["input"] == "down":
			if not self.ongoing:
				if self.survival:
					mode = "Survival"
					self.timer -= 0.5
				else:
					mode = "Blitz"
					self.timer -= 5
				self.scoreboard.text = "Mode: {}  |  Timer: {}s".format(mode, self.timer)
		elif self.ongoing:
			self.score[1] += 1
			if self.score[1] == 1:
				self.add_subview(self.scoreboard)
			s = list("CDEFGAB")
			n = len(s)
			notes = {s[i]: self.start - 0.5 * i for i in range(n)}
			guess = notes[sender["input"]]
			if abs(self.note + 3.5 - guess) <= abs(self.note - guess):
				guess -= 3.5
			self.guess = guess
			if int(2*(self.note - self.guess)) % 7 == 0:
				self.hit()
			else:
				self.miss()
			self.set_needs_display()
			
			
	def play(self):
		self.reset()
		self.remove_subview(self.instructions)
		self.remove_subview(self.scoreboard)
		self.set_needs_display()
		self.ongoing = True
		self.score = [0, 0]
		self.game.start()
		
		
	def reset(self):
		self.notes = [self.start - 0.5 * random.randint(0, 2*(self.start - self.end)) for _ in range(7)]
		self.note = self.notes[0]
		self.guess = self.note
		self.game = threading.Timer(self.timer, self.gameover)
		
		
	def gameover(self):
		self.ongoing = False
		if self.survival:
			if self.score[0] > self.best:
				self.best = self.score[0]
			self.scoreboard.text = "Streak: {}  |  Best: {}".format(self.score[0], self.best)
		self.add_subview(self.scoreboard)
		self.instructions.text = "Press [ENTER] to play again."
		self.add_subview(self.instructions)
		self.set_needs_display()
		
		
	def hit(self):
		self.score[0] += 1
		self.notes.pop(0)
		note = self.start - 0.5 * random.randint(0, 2*(self.start - self.end))
		while note == self.notes[-1]:
			note = self.start - 0.5 * random.randint(0, 2*(self.start - self.end))
		self.notes.append(note)
		self.note = self.notes[0]
		self.guess = self.notes[0]
		if self.survival:
			self.scoreboard.text = "Streak: {}".format(self.score[0])
			self.game.cancel()
			self.game = threading.Timer(self.timer, self.gameover)
			self.game.start()
		else:
			self.scoreboard.text = "Score: {} / {}; {}%".format(*self.score, round(100*self.score[0]/self.score[1]))
		
		
	def miss(self):
		if self.survival:
			self.game.cancel()
			self.gameover()
		else:
			self.scoreboard.text = "Score: {} / {}; {}%".format(*self.score, round(100*self.score[0]/self.score[1]))
		
		
	def draw(self):
		staff = ui.Image.named("treble.png")
		w, h = staff.size
		scale = h / w
		sw, sh = self.width, self.width * scale
		lh = sh / 8
		staff.draw(0, (self.height - sh)/2, sw, sh)
		
		if len(self.notes) > 0 and (self.ongoing or self.survival):
			guess = ui.Image.named("hole.png")
			w, h = guess.size
			scale = w / h
			nh = sh / 10
			nw = nh * scale
	
			if self.guess < -0.5 or self.guess > 4.5:
				if self.guess < -0.5:
					pos = -1
				else:
					pos = 5
				strike = ui.Image.named("strike.png")
				strike.draw(300, (self.height - sh)/2 + 2*nh + pos*lh, nw, nh)
							
	
			guess.draw(300, (self.height - sh)/2 + 2*nh + self.guess*lh, nw, nh)
			for i in range(len(self.notes)):
				if self.notes[i] < -0.5 or self.notes[i] > 4.5:
					if self.notes[i] < -0.5:
						pos = -1
					else:
						pos = 5
					strike = ui.Image.named("strike.png")
					strike.draw(300 + 150*i, (self.height - sh)/2 + 2*nh + pos*lh, nw, nh)
				if i == 0:
					whole = ui.Image.named("current.png")
				else:
					whole = ui.Image.named("whole.png")
				whole.draw(300 + 150*i, (self.height - sh)/2 + 2*nh + self.notes[i]*lh, nw, nh)



w, h = ui.get_screen_size()
view = MyUI(w, h)
view.present("fullscreen", hide_title_bar = True)
