from core.interpreter import interpret_one_sentence


def repl(prompt='lis.py> '):
    while True:
        try:
            val = interpret_one_sentence(raw_input(prompt)) 
        except Exception as e:
            print "syntax error"
        else:
            if val is not None: 
                print val

if __name__ == '__main__':
    repl()