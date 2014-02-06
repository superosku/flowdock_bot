import json
import getpass
import requests

class MyApp(object):
    def __init__(self):
        username = raw_input("Username: ")
        password = getpass.getpass()
        self.auth = (username, password)
        self.users = {}
        self.word_list = []
    def send_message(self, content):
        print "Sending message:", content
        url = ('https://api.flowdock.com/flows/'+self.flow['organization']['parameterized_name']+'/'+self.flow['parameterized_name']+'/messages/')
        data = {'event': 'message', 'content': content}
        res = requests.post(url, auth=self.auth, data=data)
    def get_user(self, ident):
        if ident not in self.users:
            print "User not saved, gettin user data"
            url = ('https://api.flowdock.com/users/'+ident)
            res = requests.get(url, auth=self.auth)
            self.users[ident] = res.json()
        return self.users[ident]
    def handle_commands(self, line):
        words = line.split()
        content = "Command not regonized"
        if words[0] == "!addword":
            print "Word added"
            content = "Words added: "
            for word in words[1:]:
                if word not in self.word_list:
                    self.word_list.append(word)
        elif words[0] == "!removeword":
            print "Removing words"
            content = "Words removed"
            for word in words[1:]:
                if word in self.word_list:
                    self.word_list.remove(word)
        elif words[0] == "!list":
            content = "Words: " + ", ".join(self.word_list)
        self.send_message(content)

    def run(self):
        print "Getting flows"
        res = requests.get('https://api.flowdock.com/flows/all',
                auth=self.auth)
        self.my_user_id = res.headers['Flowdock-User']
        flows_json = res.json()
        for i, x in enumerate(flows_json):
            print "{} : {}".format(i, x['name'])
        self.flow = flows_json[int(raw_input("Choose flow: "))]
        res = requests.get('https://stream.flowdock.com/flows/', 
                auth=self.auth, 
                stream=True,
                params={'filter':self.flow['id']})

        print "Listening.."
        for line in res.iter_lines():
            if line:
                json_line = json.loads(line)
                user = json_line['user']
                if json_line['event'] == 'message' and user != self.my_user_id:
                    content = json_line['content']
                    if len(content) > 0 and content[0] == '!':
                        self.handle_commands(content)
                    else:
                        print "Message event", content
                        for word in self.word_list:
                            if content.find(word) >= 0:
                                print "Word found, sending message"
                                message = self.get_user(user)['nick'] + " said word: " + word
                                self.send_message(message)
                                break
                else:
                    print "Other event"

if __name__ == '__main__':
    app = MyApp()
    app.run()

