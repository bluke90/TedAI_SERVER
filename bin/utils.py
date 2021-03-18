from sys import stdout as std


def cout(string):
    return std.write(string)

# parse dictionaries and return each line as "=" sepereated dictionary
def data_parse(data):
    dictionary = {}
    data = data.split('\n')
    for line in data:
        if line != "" and line != " ":
            line = line.split(' = ')
            dictionary[line[0]] = line[1]

    return dictionary


# Handle color of console text
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[32m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

