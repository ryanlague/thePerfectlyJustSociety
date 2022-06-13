class Style:
    @classmethod
    def _style(cls, base, **kwargs):
        style = base.copy()
        style.update(kwargs)
        return style

    @classmethod
    def section(cls, **kwargs):
        return cls._style(
            {'display': 'flex', 'flex-direction': 'column', 'flex-wrap': 'wrap',
             'width': '100%', 'max-height': '2000px', 'text-align': 'center',
             'justify-content': 'center', 'align-items': 'flex-start',
             'transition-delay': '3s', 'transition-property': 'all'},
            **kwargs)

    @classmethod
    def paramBox(cls, **kwargs):
        return cls._style({'height': '300px', 'width': '500px', 'border-style': 'solid',
                           'margin': '10px auto 10px auto', 'overflow': 'hidden',
                           'transition-duration': '3s', 'transition-property': 'all'},
                          **kwargs)

    @classmethod
    def container(cls, **kwargs):
        return cls._style(
            {'width': '100%', 'display': 'flex', 'flex-direction': 'row', 'flex-wrap': 'wrap',
             'align-items': 'center', 'transition-duration': '3s'}, **kwargs)

    @classmethod
    def text(cls, **kwargs):
        return cls._style({'flex-basis': '100%', 'text-align': 'center', 'margin-top': '0px', 'margin-right': '0px',
                           'margin-bottom': 'auto'}, **kwargs)

    @classmethod
    def inputWrapper(cls, textAlign='center',
                     marginTop='auto', marginRight='auto', marginLeft='auto', marginBottom='10px',
                     width='220px', flexBasis='40%', **kwargs):
        return cls._style({
            'text-align': textAlign,
            'margin-top': marginTop, 'margin-right': marginRight,
            'margin-bottom': marginBottom, 'margin-left': marginLeft,
            'width': width, 'flex-basis': flexBasis
        }, **kwargs)

    @classmethod
    def button(cls, **kwargs):
        return cls._style({'text-align': 'center', 'margin-bottom': '10px', 'margin-left': 'calc(50% - 110px)',
                           'width': '220px'}, **kwargs)

    @classmethod
    def button2(cls, textAlign='center',
                marginTop='auto', marginRight='auto', marginLeft='auto', marginBottom='10px',
                width='220px', flexBasis='40%', **kwargs):
        return cls._style({
            'text-align': textAlign,
            'margin-top': marginTop, 'margin-right': marginRight,
            'margin-bottom': marginBottom, 'margin-left': marginLeft,
            'width': width, 'flex-basis': flexBasis
        }, **kwargs)

    @classmethod
    def cancel(cls, **kwargs):
        return cls._style({'font-size': '18px', 'padding': '5px',
                           'margin': '0', 'margin-top': '-20px', 'margin-bot': '0', 'margin-left': '-80px',
                           'text-align': 'left',
                           'line-height': '100%', 'vertical-align': 'center', 'border': 'none'}, **kwargs)

    @classmethod
    def icon(cls, **kwargs):
        return cls._style({'font-size': '18px', 'padding': '5px',
                           'margin-top': '5px', 'margin-right': '5px', 'margin-bottom': 'auto', 'margin-left': 'auto',
                           'text-align': 'right',
                           'line-height': '100%', 'vertical-align': 'center', 'border': 'none', 'z-index': '1'},
                          **kwargs)

    @classmethod
    def progress(cls, marginTop='-50px', marginRight='auto', marginBottom='auto', marginLeft='auto',
                 height='40px', lineHeight='40px', display='flex', flexDirection='row',
                 alignItems='center', justifyContent='center',
                 **kwargs):
        return cls._style({'margin-top': marginTop, 'margin-right': marginRight,
                           'margin-bottom': marginBottom, 'margin-left': marginLeft,
                           'height': height, 'max-width': '50%', 'line-height': lineHeight, 'display': display,
                           'flex-direction': flexDirection,
                           'align-items': alignItems, 'justify-content': justifyContent}, **kwargs)

    @classmethod
    def dropdown(cls, **kwargs):
        return cls._style({'margin': 0, 'padding': 0}, **kwargs)

    @classmethod
    def graph(cls, **kwargs):
        return cls._style({'margin': 0, 'padding': 0, 'margin-top': '0px'}, **kwargs)
