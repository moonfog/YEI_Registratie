def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))


def new():

    if len(guest_errors)==0:

        form = SQLFORM(db.guest,fields=['firstname','familyname','sex','birth_year','national_number']) ##,hidden=dict(shw=auth.user.id))
        #form.vars.user = auth.user.id
        form[0][-1][1].append(TAG.INPUT(_value=T('Cancel'),_type="button",_onclick="window.location='%s';"%URL(r=request,f='overview')))
        if form.process().accepted:
            max = db.guest.id.max()
            guestId=db().select(max).first()[max]
            session.guestID=guestId
            session.guest_inserted=1
            redirect(URL(r=request,f='overview'))
        elif form.errors:
           response.flash = T('form has errors')

        else:
            response.flash = T('Create new guest')

        return dict(form=form)

    else:
        session.type_error='guest'
        redirect(URL(r=request,c='error',f='category_value'))
