URLS_LITE = {
    '/new_waifu': (
        'https://api.waifu.im/search/',
        'Waifu'
    ),
    '/maid': (
        'https://api.waifu.im/search/?&included_tags=maid',
        'Maid'
    ),
    '/raiden_shogun': (
        'https://api.waifu.im/search/?included_tags=raiden-shogun',
        'Raiden_shogun'
    ),
    '/uniform': (
        'https://api.waifu.im/search/?gif=false&included_tags=uniform',
        'Uniform',
    ),
}

BUTTON_LITE = (
        ['/clear_history'],
        ['/uniform', '/maid', ],
        ['/raiden_shogun', '/new_waifu', ],

)

BOT_COMMANDS_LITE = [
    'maid',
    'raiden_shogun',
    'uniform',
    'new_waifu',
]
