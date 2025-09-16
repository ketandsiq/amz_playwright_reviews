from scrapy import Selector

class AttributeParser:
  def json_value_parser(self, itemlist, json_data):
    test = json_data
    if isinstance(itemlist[0], list):  # this the case of going inside the nested structure of the json to get the value safely
      for item in itemlist:
        for sub_item in item:
          if isinstance(json_data, dict) and sub_item in json_data:
              json_data = json_data[sub_item]  # Move inside the json structure
              break  # Stop to again start with new json structure
      if json_data and json_data != test:  # in last the value is in the json_data variable so we have to return
        return json_data
      else: return None
    else:  # without nesting case
      for item in itemlist:
        value = json_data.get(item)
        if value:
          return value
    return None  # Return None if no valid value is found

  def css_value_parser(self, itemlist, response):
    for item in itemlist:
      if isinstance(item, list): # this is case where we want to combine multiple div or span to get the final value 
        final_value = [] # returning the final value list so that in spider we can join them with space or any other separator
        for sub_item in item:
          for final_item in sub_item:
            value = response.css(final_item).get()
            if value:
              final_value.append(value.strip())
        if final_value:
          return final_value
      else:
        value = response.css(item).get()
        if value:
          return value.strip()
      
  def css_card_list(self, itemlist, response):
    for item in itemlist:
        value = response.css(item).getall()
        if value:
          converted_value = [Selector(text=v) for v in value]
          return converted_value
    
  def css_getall_values_parser(self, itemlist, response):
    for item in itemlist:
        value = response.css(item).getall()
        if value:
          return [val.replace('\u200e', '').replace('\u200f','').replace('\n','').strip() for val in value] # remove the leading and trailing spaces from the values and also the unicode char 
  def xpath_value_parser(self, itemlist, response):
    for item in itemlist:
      value = response.xpath(item).get()
      if value:
          return value
  def xpath_getall_values_parser(self, itemlist, response):
    for item in itemlist:
      value = response.xpath(item).getall()
      if value:
          return value
  def xpath_selector_list(self, itemlist, response):
    for item in itemlist:
      value = response.xpath(item)
      if value:
        return value