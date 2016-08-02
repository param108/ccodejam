from django.template.defaulttags import register

@register.filter
def dictget(dictionary, key):
  return dictionary.get(key)

@register.filter
def getsmallstatus(dictionary, key):
  val = dictionary.get(key)
  if not val:
    return None
  print val[0].result
  return val[0].result

@register.filter
def getlargestatus(dictionary, key):
  val = dictionary.get(key)
  if not val:
    return None
  print val
  if len(val) == 2:
    print val[1].result
    return val[1].result
  else:
    return "No large Set for this question"
