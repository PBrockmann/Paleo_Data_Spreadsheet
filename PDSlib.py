#==========================================================
# Patrick Brockmann - LSCE
# 2015/10/11
#==========================================================

# TODO: - implement handling of erros with try/except and return values
 
#==========================================================
import pandas as pd
import datetime
import collections

#==========================================================
def PDS_to_df(file):

    dfD = pd.read_excel(file, sheetname='Data')
    dfM = pd.read_excel(file, sheetname='Metadata', header=None, names=['Attribute', 'Value'])

    return dfD, dfM 

#==========================================================
def df_to_PDS(file, dfD, dfM):

    writer = pd.ExcelWriter(file)

    dfD.to_excel(writer, sheet_name="Data", index=False)                 
    dfM.to_excel(writer, sheet_name="Metadata", index=False, header=False)

    writer.save()

#=========================================================
def df_to_LiPD(dfD, dfM, verbose=True):
    
    dict_out = collections.OrderedDict()

    parameters = dfD.columns

    for index, row in dfM.iterrows() :
        #print row['Attribute']
        attributes = row['Attribute'].split('.')
    
        parameter = attributes[0]
        if len(attributes) == 1:
            if parameter in parameters:
                if verbose:
                    print 'df_to_LiPD: Warning: at line %4d : %s is a parameter with no attribute => line ignored' \
                                        %(index+1, parameter)
                continue
        else:
            if parameter not in parameters:
                if verbose:
                    print 'df_to_LiPD: Warning: at line %4d : %s not present in Data worksheet' \
                                        %(index+1, parameter)

        d = dict_out
        for attribute in attributes[0:-1] :
            d = d.setdefault(attribute, {})
        
        if d.get(attributes[-1]) != None:
            if verbose:
                print 'df_to_LiPD: Warning: at line %4d : %s already set with value %s => overwritten with new value %s' \
                                        %(index+1, row['Attribute'], d.get(attributes[-1]), row['Value'])
            
        if row['Value'] == "True" :
            row['Value'] = True
        if row['Value'] == "False" :
            row['Value'] = False
        if isinstance(row['Value'], datetime.datetime):
            row['Value'] = row['Value'].isoformat()

        d[attributes[-1]] = row['Value']
        
    return dict_out

#========================================================== 
def dotnotation_for_nested_dictionary(d, key, dots):
    
    if isinstance(d, dict):
        for k in d:
            dotnotation_for_nested_dictionary(d[k], key + '.' + k if key else k, dots)
    elif isinstance(d, list) and \
            not all(isinstance(item, (int, long, float, complex, list)) for item in d):
        for n,d in enumerate(d):
            dotnotation_for_nested_dictionary(d, key + '.' + str(n) if key != "" else key, dots)
    else:
        dots[key]=d 
        
    return dots

#==========================================================
def LiPD_to_df(dict_in):
    
    dict_in_dotted=collections.OrderedDict()
    dotnotation_for_nested_dictionary(dict_in, '', dict_in_dotted)

    dfM=pd.DataFrame(dict_in_dotted.items(), columns=['Attribute', 'Value'])
    try:
    	dfD=pd.read_csv(dict_in['filename'])
    except:
	dfD=pd.DataFrame()
    
    return dfD, dfM

#==========================================================
def PDS_to_LiPD(file, verbose=True):

    dfD, dfM = PDS_to_df(file)
    
    dict_out = df_to_LiPD(dfD, dfM, verbose=verbose)
    
    return dict_out

#==========================================================
def LiPD_to_PDS(dict_in, file):

    dfD, dfM = LiPD_to_df(dict_in)

    df_to_PDS(file, dfD, dfM)

#==========================================================
