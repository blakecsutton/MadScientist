from django.contrib.admin import widgets
from django.forms.widgets import CheckboxSelectMultiple, CheckboxInput, Select
from django.forms import CharField
from django.utils.datetime_safe import datetime
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from itertools import chain
from django.db.models import Count
from models import Facet, Tag

# Logging
import logging
logger = logging.getLogger(__name__)

class FacetedColumnCheckboxSelectMultiple(CheckboxSelectMultiple):
    """ This is a widget that accepts a list of tags and displays them in individual spans
        grouped by parent Facet, with the Facet name displayed at the top of each span.
        Facets with no tags assigned to them are ignored and not displayed, and if there are
        tags that have no parent Facet those tags are all assigned to an "Uncategorized"
        facet and displayed that way.
        
        This widget only modifies the display, it does not affect the way the tags are handled
        on the back end. However, this widget is obviously specific to my model design.
    """
    
    def render(self, name, value, attrs=None, choices=()):
      
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        
        output = []
        
        # Get a list of all facets with tags attached and the number of tags in each one.
        facets = Facet.objects.annotate(size=Count('tag')).filter(**{'size__gt': 0}).values('name', 'size', 'group__short_title')
        
        # Get a list of all tags without a facet and format it so we can easily check it against id
        unfaceted_tags = Tag.objects.filter(facet=None)
        unfaceted_tag_ids = unfaceted_tags.values_list('id')
        unfaceted_tag_ids = [value[0] for value in unfaceted_tag_ids]
        unfaceted = unfaceted_tags.count()
        
        # If there are tags without a facet, make an Uncategorized facet and put it first
        facet_list = []
        if unfaceted > 0:
            facet_list.append({'name': 'Uncategorized',                              
                          'size': unfaceted,
                          'group__short_title': 'Various',
                          'start': 0})
        elif len(facets) > 0:
            # If starting with the first facet, need to set up the start index of the 0'th index
            facets[0]['start'] = 0
        
        # Append all the facets to the list, which might or might not start with an uncategorized facet
        for f in facets:
            facet_list.append(f)
        
        # Calculate which indices are the end of the facets
        for current in range(1, len(facet_list)):
            facet_list[current]['start'] = facet_list[current-1]['start'] + facet_list[current-1]['size']
         
        # If there are facets or tags without a facet, display the first header before printing the tags
        style = u"<span style='width: 150px; float: left; padding: 10px;'><h3>%s (%s)</h3>"
        facet_index = 0
        if facet_index < len(facet_list) :
            
            output.append(style % (facet_list[facet_index]['name'], facet_list[facet_index]['group__short_title']))
            facet_index += 1
            
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
          
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''
            
            # Check the current item index against the start indices of each facet to
            # decide whether to print the label heading and start a new span column
            if facet_index < len(facet_list) and i == facet_list[facet_index]['start']:
                
                output.append(u'</span>')
                output.append(style % (facet_list[facet_index]['name'], facet_list[facet_index]['group__short_title']))
                facet_index += 1
            
            # See if the current option's id is in the list of tags with no facet
            if option_value in unfaceted_tag_ids:
              
              # Look up the actual model object so we can get the group info.
              tag_model = Tag.objects.get(pk=option_value)
              # Get group name of the tag to display after the tag name
              option_label += " ({})".format(tag_model.group.short_title)

            # Actually create the checkbox here. Value/str_values is the previously selected items.
            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            
             
            # Hackity hack, added display: block styling to make each tag checkbox appear on own line.
            output.append(u"<span style='display: block'><label%s>%s %s</label></span>" % (label_for, rendered_cb, option_label))
            
        output.append(u'</span>')  
    
        return mark_safe(u'\n'.join(output))
