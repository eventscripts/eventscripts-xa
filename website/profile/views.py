"""
Profile views
"""
from xa.utils import render_to

@render_to
def edit(request):
    """
    Simple edit profile view
    """
    return 'profile/edit.htm', {}
