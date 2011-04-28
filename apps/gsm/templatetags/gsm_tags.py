from django import template

from gsm.models import GsmEntity

register = template.Library()

@register.tag(name='gsm_entity')
def do_gsm_entity(parser, token):
    """
    Required arguments:
    - key: the context key to set with the resulting GsmEntity
    - (tag and gsm_id) or element:
        - element is an lxml element
        - tag is a gsm tag name (match, season...)
        - gsm_id is the remote id

    Two minimal usage examples:
    
    {% gsm_entity element=foo key=bar %}
    Makes a GsmEntity for element foo, global sport, in {{ bar }}

    {% gsm_entity tag=match gsm_id=123 key=bar %}
    Makes a GsmEntity for tag 'match' with gsm_id 123 in {{ bar }}
    """
    arguments = {}
    for arg in token.split_contents()[1:]:
        equal = arg.find('=')
        if equal:
            arguments[arg[:equal]] = arg[equal+1:]
        else:
            arguments[arg] = True
        
    if 'key' not in arguments:
        raise template.TemplateSyntaxError("gsm_entity requires a key argument (UTSL)")
    
    if 'element' not in arguments:
        if 'tag' not in arguments and 'gsm_id' not in arguments:
            raise template.TemplateSyntaxError("gsm_entity requires either element or both tag and gsm_id arguments (UTSL)")

    return GsmEntityNode(**arguments)

class GsmEntityNode(template.Node):
    def __init__(self, **kwargs):
        """ OMG UGLY VOODOO """
        for k, v in kwargs.items():
            try:
                is_int = str(int(v)) == v
            except:
                is_int = False

            if v[0] == '"' or v[0] == "'":
                setattr(self, k, v[1:-1])
            elif is_int:
                setattr(self, k, v)
            else:
                setattr(self, k, template.Variable(v))
    
    def render(self, context):
        if hasattr(self, 'element'):
            element = self.element.resolve(context)
            entity = GsmEntity(
                sport = context['sport'],
                gsm_id = element.attrib['%s_id' % element.tag],
                tag = element.tag
            )
            entity.element = element
        else:
            # not bloating with layers for now, refactor when required
            if hasattr(self.tag, 'resolve'):
                tag = self.tag.resolve(context)
            else:
                tag = self.tag

            if hasattr(self.gsm_id, 'resolve'):
                gsm_id = self.gsm_id.resolve(context)
            else:
                gsm_id = self.gsm_id

            entity = GsmEntity(
                sport = context['sport'],
                gsm_id = gsm_id,
                tag = tag
            )

        if hasattr(self.key, 'resolve'):
            key = self.key.resolve(context)
        else:
            key = self.key

        context[key] = entity

        return ''
