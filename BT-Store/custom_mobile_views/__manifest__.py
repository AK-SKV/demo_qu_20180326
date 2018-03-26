# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 brain-tec AG (http://www.braintec-group.com)
# All Right Reserved
#
# See LICENSE file for full licensing details.
##############################################################################

{
    'name': "Customized views for mobiles",
    'summary': "Allows to define views to be used when the device is a mobile",
    'description': """
This module allows to change standard views when the browser is a mobile:
 - Create a view with the type you want to customize
 - Activate the field "Should be used for mobiles?"

 Contributors (logos)
 --------------------

 Pelfusion: http://www.pelfusion.com/
   - http://www.iconarchive.com/show/long-shadow-media-icons-by-pelfusion/Mobile-Smartphone-icon.html

 Garrett Knoll, from The Noun Project [CC BY 3.0 us (http://creativecommons.org/licenses/by/3.0/us/deed.en)], via Wikimedia Commons
   - https://commons.wikimedia.org/wiki/File:Edit_icon_(the_Noun_Project_30184).svg

 By Fouky (Own work) [Public domain], via Wikimedia Commons
   - https://commons.wikimedia.org/wiki/File:%C3%89cran_TV_plat.svg

 Uyen, from The Noun Project [CC BY 3.0 us (http://creativecommons.org/licenses/by/3.0/us/deed.en)], via Wikimedia Commons
   - https://commons.wikimedia.org/wiki/File:Smartphone_icon_-_Noun_Project_283536.svg

 It requires the following python packages:

 - pip install pyyaml ua-parser user-agents

    """,
    'author': "brain-tec",
    'website': "http://www.braintec-group.com/",
    'category': 'Extra Tools',
    'version': '10.0.1.0.0',
    'price': 9.99,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images': [
        'static/description/main_screenshot.png',
    ],
    'external_dependencies': {
        'python': [
            'user_agents',
            'ua_parser',
            'yaml',
        ],
    },
    'depends': [
        'base'
    ],
    'data': [
        'views/ir_ui_view_views.xml',
    ],
    'js': [],
}
