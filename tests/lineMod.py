# line mod function

def lineMod(line,par,par_value):
    rep_value = str(par_value)+str('\n')
    if par in line:
        orig_value = str(line.split(' = ')[1])
        rep_line = line.replace(orig_value,rep_value)
        return rep_line
    else:
        return None
