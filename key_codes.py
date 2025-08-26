# macOS Virtual Key Codes
# Sourced from various online resources and Apple's documentation.

class KeyCodes:
    # --- Alphanumeric Keys ---
    a = 0x00
    s = 0x01
    d = 0x02
    f = 0x03
    h = 0x04
    g = 0x05
    z = 0x06
    x = 0x07
    c = 0x08
    v = 0x09
    b = 0x0B
    q = 0x0C
    w = 0x0D
    e = 0x0E
    r = 0x0F
    y = 0x10
    t = 0x11
    k_1 = 0x12
    k_2 = 0x13
    k_3 = 0x14
    k_4 = 0x15
    k_6 = 0x16
    k_5 = 0x17
    equal = 0x18  # =
    k_9 = 0x19
    k_7 = 0x1A
    minus = 0x1B  # -
    k_8 = 0x1C
    k_0 = 0x1D
    right_bracket = 0x1E  # ]
    o = 0x1F
    u = 0x20
    left_bracket = 0x21  # [
    i = 0x22
    p = 0x23
    l = 0x25
    j = 0x26
    quote = 0x27  # '
    k = 0x28
    semicolon = 0x29  # ;
    backslash = 0x2A  # \
    slash = 0x2C  # /
    n = 0x2D
    m = 0x2E
    period = 0x2F  # .
    grave = 0x32  # `
    keypad_decimal = 0x41  # .
    keypad_multiply = 0x43  # *
    keypad_plus = 0x45  # +
    keypad_clear = 0x47  # Clear
    keypad_divide = 0x4B  # /
    keypad_enter = 0x4C  # Enter
    keypad_minus = 0x4E  # -
    keypad_equals = 0x51  # =
    keypad_0 = 0x52
    keypad_1 = 0x53
    keypad_2 = 0x54
    keypad_3 = 0x55
    keypad_4 = 0x56
    keypad_5 = 0x57
    keypad_6 = 0x58
    keypad_7 = 0x59
    keypad_8 = 0x5B
    keypad_9 = 0x5C

    # --- Function Keys ---
    f5 = 0x60
    f6 = 0x61
    f7 = 0x62
    f3 = 0x63
    f8 = 0x64
    f9 = 0x65
    f11 = 0x67
    f13 = 0x69
    f16 = 0x6A
    f14 = 0x6B
    f10 = 0x6D
    f12 = 0x6F
    f15 = 0x71
    help = 0x72
    f1 = 0x7A
    f2 = 0x78
    f4 = 0x76

    # --- Control Keys ---
    return_key = 0x24
    tab = 0x30
    space = 0x31
    delete = 0x33
    escape = 0x35
    command = 0x37
    shift = 0x38
    caps_lock = 0x39
    option = 0x3A
    control = 0x3B
    right_shift = 0x3C
    right_option = 0x3D
    right_control = 0x3E
    function = 0x3F

    # --- Arrow Keys ---
    left_arrow = 0x7B
    right_arrow = 0x7C
    down_arrow = 0x7D
    up_arrow = 0x7E

    # --- Other Keys ---
    home = 0x73
    page_up = 0x74
    forward_delete = 0x75
    end = 0x77
    page_down = 0x79