
#ANSI COLORS FOR XTERM
CRES=chr(27)+"[0m"
CBOLD=chr(27)+"[1m"
CBLACK=chr(27)+"[38;5;0m"
CRED=chr(27)+"[38;5;1m"
CGRN=chr(27)+"[38;5;2m"
CYELLO=chr(27)+"[38;5;3m"
CBLUE=chr(27)+"[38;5;4m"
CMAG=chr(27)+"[38;5;5m"
CCYAN=chr(27)+"[38;5;6m"
CWHITE=chr(27)+"[38;5;7m"
CBBLACK=chr(27)+"[38;5;8m"
CBRED=chr(27)+"[38;5;9m"
CBGRN=chr(27)+"[38;5;10m"
CBYELLO=chr(27)+"[38;5;11m"
CBBLUE=chr(27)+"[38;5;12m"
CBMAG=chr(27)+"[38;5;13m"
CBCYAN=chr(27)+"[38;5;14m"
CBWHITE=chr(27)+"[38;5;15m"
#END OF COLORS

def mcolor(col,msg,ucolo=None):
    """
        M(ake_)color function

        :param col: Variable name of the color to apply. "default" for default color.
        :param msg: The message to apply color to.
        :param ucolo: Whether to check if user has colors enabled.
        
    """
    # Leaving the default color as it is.
    if col=="default": return msg
    if ucolo["enabled"]==True:
        # We are checking user settings.
        return col+msg+CRES
    elif ucolo["enabled"]==False:
        return msg
    elif ucolo==None:
        # User settings is not our business.
        return col+msg+CRES
    else:
        return msg

