from xa.utils import render_to

@render_to
def edit(request):
    return 'profile/edit.htm', {}
