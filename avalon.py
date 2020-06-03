import api_zoom
import random, os, time, pickle, sys, importlib
from datetime import datetime
import config

get = api_zoom.get
post_json = api_zoom.post_json
def avalon_help():
    print('''
General help:
    avalon_help() #this message
    reload_config() #reload the config module
    contacts() # list zoom contacts
    reload_token() #reload token if expires
Game:
    a.setup(game_num) # randomly assign roles based on config file
    a.names() #print names after setup
    a.save() #save setup
    a.load() #load setup
    a.send_test() #send test message to everybody
    a.send_roles() #send to everybody - should be done just once after calling setup()
    a.send_vote(vote_num) #send vote
    a.send_quest(questers,quest_num)
    a.send_quest_results(quest_num)
        ''')
def reload_config():
    importlib.reload(config)
    

def contacts():
    r = get('/chat/users/me/contacts?type=company')
    for contact in r.json()['contacts']:
        print(contact['first_name'] + ' ' + contact['last_name'] + ' : ' + contact['email'])
    time.sleep(1)
    r = get('/chat/users/me/contacts?type=external')
    for contact in r.json()['contacts']:
        print(contact['first_name'] + ' ' + contact['last_name'] + ' : ' + contact['email'])
def reload_token():
    with open('token.pcl','rb') as f:
        token_response = pickle.load(f)
    token_data = token_response.json()
    access_token = token_data['access_token']
    api_zoom.token_response = token_response
    api_zoom.token_data = token_data
    api_zoom.access_token = access_token


class Avalon():
    def __init__(self):
        #check token
        user = get('users/me')
        print('Logged in as %s' % user.json()['email'])
    def save(self):
        state = (self.date,self.game_num,self.vote_codes,self.quest_codes,self.assignments)
        with open('save.pcl','wb') as f:
            pickle.dump(state,f)
    def load(self):
        with open('save.pcl','rb') as f:
            state = pickle.load(f)
        self.date,self.game_num,self.vote_codes,self.quest_codes,self.assignments = state

    def setup(self,game_num,vote_codes=None,quest_codes=None):
        self.date = datetime.now().strftime('%b %d')
        self.game_num = game_num
        if vote_codes is None:
            vote_codes = config.vote_codes
        self.vote_codes = vote_codes
        if quest_codes is None:
            quest_codes = config.quest_codes
        self.quest_codes = quest_codes

        players = config.players
        num_players = len(players)
        if not (5 <= num_players <= 10):
            raise Exception('Number of players must be between 5 and 10 inclusive')
        good_evil_table = {5:(3,2),6:(4,2),7:(4,3),8:(5,3),9:(6,5),10:(6,4)}
        num_good,num_evil = good_evil_table[num_players]
        roles = ['Merlin','Assassin']+['Loyal Servant of Arthur']*(num_good-1) + ['Minion of Mordred']*(num_evil-1)
        random.seed()
        random.shuffle(players)
        random.shuffle(roles)
        assignments = []
        minions = []
        for (name,email),role in zip(players,roles):
            assignments.append([name,email,role])
            if role == 'Minion of Mordred' or role == 'Assassin':
                minions.append(name)
        minions.sort()
        for record in assignments:
            name,email,role = record
            if role == 'Merlin':
                message = '''Avalon {date} Game {game_num}
{name},
You are Merlin. Of the loyal servants of Arthur, you alone know the true faces of the agents of Evil. 
You must use your hidden knowledge very carefully, as the Assassin is searching for your true identity.
If the Assassin finds you, all will be lost.
The Minions of Mordred are: {minions}
    '''.format(date=self.date,game_num=game_num,name=name,minions=', '.join(minions))
            elif role == 'Assassin':
                message = '''Avalon {date} Game {game_num}
{name},
You are the Assassin. The Master has personally entrusted you with eliminating one of the greatest threats to his power: the false prophet known as Merlin. Use what you have learned from years of brutal training to keep a keen eye out for signs of the charlatan's trickery.
Should the other minions of Mordred fail to sabotage the quests for the Holy Grail, your identification and assassination of Merlin is Evil's last chance.
The Minions of Mordred are: {minions}
    '''.format(date=self.date,game_num=game_num,name=name,minions=', '.join(minions))
            elif role == 'Loyal Servant of Arthur':
                message = '''Avalon {date} Game {game_num}
{name},
You are a loyal servant of Arthur, the true king of Britain and the last hope for prosperity and honor in a land rampant with evil.
Be careful who you trust as the minions of the would-be usurper Mordred are slithering amongst the court of Camelot.
Keep your eyes open for signs of treachery and use your influence at the round table to isolate the betrayers and prevent them from sabotaging the sacred quest for the Holy Grail.
    '''.format(date=self.date,game_num=game_num,name=name)
            elif role == 'Minion of Mordred':
                message = '''Avalon {date} Game {game_num}
{name},
You are a Minion of Mordred, the strong son of a weak king and the only man with power and vision to carry Britain into a glorious New World Order. 
You must infiltrate the round table and use your influence to sabotage Arthur's attempts to obtain the Holy Grail.
Without the power of the grail, Arthur's forces shall surely fail. For your service to the Master, you are promised a title as a lord of the new realm.
The Minions of Mordred are: {minions}
    '''.format(date=self.date,game_num=game_num,name=name,minions=', '.join(minions))
            else:
                raise Exception('Unexpected role: %s' % role)
            record.append(message)
        self.assignments = assignments

    def names(self):
        for name,email,role,message in self.assignments:
            print(name)

    def send_test(self):
        for name,email,role,message in self.assignments:
            print('Sending to ' + name)
            post_json('/chat/users/me/messages',{'message':'Test message for Avalon','to_contact':email})
            time.sleep(1)

    def send_roles(self):
        for name,email,role,message in self.assignments:
            print('Sending to ' + name)
            post_json('/chat/users/me/messages',{'message':message,'to_contact':email})
            time.sleep(1)
    def send_vote(self,questers,vote_num):
        vote_view_code, vote_approve_code, vote_reject_code = self.vote_codes

        vote_message = '''Avalon {date} Game {game_num} Vote {vote_num}

Quest Proposal: {questers}

View Results
https://pollie.app/{view_code}

Click a link to vote:
    
Approve
https://pollie.app/{approve_code}

Reject
https://pollie.app/{reject_code}
'''.format(questers=', '.join(questers),date=self.date,game_num=self.game_num,vote_num=vote_num,view_code=vote_view_code,approve_code=vote_approve_code,reject_code=vote_reject_code)
        for name,email,role,message in self.assignments:
            print('Sending to ' + name)
            post_json('/chat/users/me/messages',{'message':vote_message,'to_contact':email})
            time.sleep(1)

    def send_quest(self,questers,quest_num,quest_codes=None):
        names = set([item[0] for item in self.assignments])
        questers = set(questers)
        if not (questers <= names):
            raise Exception('Not all names provided are valid')
        if quest_codes is None:
            if not quest_num in self.quest_codes:
                raise Exception('quest codes do not exist for quest number')
            quest_view_code,quest_success_code,quest_fail_code = self.quest_codes[quest_num]
        else:
            quest_view_code,quest_success_code,quest_fail_code = quest_codes
        quester_message = '''Avalon {date} Game {game_num} Quest {quest_num}
Click a link to select your decision for the Quest:
    
Success
https://pollie.app/{success_code}

Fail
https://pollie.app/{fail_code}

Loyal Servants of Arthur (including Merlin) must always choose Success.
Minions of Mordred (including the Assassin) may choose Success or Fail.
'''.format(date=self.date,game_num=self.game_num,quest_num=quest_num,success_code=quest_success_code,fail_code=quest_fail_code)
        for name,email,role,message in self.assignments:
            if name in questers:
                print('Sending to ' + name)
                post_json('/chat/users/me/messages',{'message':quester_message,'to_contact':email})
                time.sleep(1)
    def send_quest_results(self,quest_num,quest_codes=None):
        if quest_codes is None:
            if not quest_num in self.quest_codes:
                raise Exception('quest codes do not exist for quest number')
            quest_view_code,quest_success_code,quest_fail_code = self.quest_codes[quest_num]
        else:
            quest_view_code,quest_success_code,quest_fail_code = quest_codes
        nonquester_message = '''Avalon {date} Game {game_num} Quest {quest_num}
View Quest Results
https://pollie.app/{view_code}
'''.format(date=self.date,game_num=self.game_num,quest_num=quest_num,view_code=quest_view_code)
        for name,email,role,message in self.assignments:
            print('Sending to ' + name)
            post_json('/chat/users/me/messages',{'message':nonquester_message,'to_contact':email})
            time.sleep(1)
if __name__ == '__main__':
    os.environ['PYTHONINSPECT'] = '1'
    a = Avalon()
    avalon_help()
