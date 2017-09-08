class Review:
	def __init__(self, source, reviewid, date, title, role, location, recommend, summary, pros, cons, advicetomgt):
		self.source = source
		self.reviewid = reviewid
		self.date = date
		self.title = title
		self.role = role
		self.location = location
		self.recommend = recommend
		self.summary = summary
		self.pros = pros
		self.cons = cons
		self.advicetomgt = advicetomgt
	#enddef
	'''
	def __init__(self, date, role, gotOffer, experience, difficulty, length, details, questions):
		self.date = date
		self.role = role
		self.gotOffer = gotOffer
		self.experience = experience
		self.difficulty = difficulty
		self.length = length
		self.details = details
		self.questions = questions
		'''