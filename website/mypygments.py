from pygments.lexer import RegexLexer, bygroups
from pygments.token import *
import re
    

class EventScriptsLexer(RegexLexer):
    """
    Lexer for code written in EventScripts Classic, the scripting language for
    Mattie's EventScripts.
    """
    name = 'EventScripts'
    aliases = ['es', 'eventscripts', 'esc']
    filenames = ['*es_*.txt']
    flags = re.DOTALL
    tokens = {
        'root': [
            (r'//.*?\n', Comment),
            (r'(event )(\w+)',
             bygroups(Keyword.Constant, Name.Function)),
            (r'(block )(\w+)',
             bygroups(Keyword.Constant, Name.Function)),
            (r'[{}()]+', Punctuation),
            (r'e(ventscript)?s(_| )\w+', Keyword),
            (r'est_\w+', Keyword.Pseudo),
            (r'(event_var)(\()(\w+)(\))',
             bygroups(Keyword.Constant, Punctuation, Name.Variabel, Punctuation)),
            (r'(server_var)(\()(\w+)(\))',
             bygroups(Keyword.Constant, Punctuation, Generic, Punctuation)),
            (r'\d+\.?\d*', Number),
            (r'"[^"]+"', String.Double),
            (r'(true|false)', Keyword.Constant),
            (r'(average|cheatexec|clientcmd|damage|downloadable|if|else|do|then|esnq|forcecase|foreach|getbotname|getplayercount|getplayerinfo|getrandplayer|ifx|inrange|isnull|isnumerical|keyfilter|keygrouprand|keygroupremove|keygroupsort|keymath|keymenu|popup|vecmath|sqlx|stack|statlog|usermsg|while|playerget|playerset|queue|linkedlist|nearcord|profile|profilecmd)', Keyword),
            (r'.', Generic),
        ],
    }