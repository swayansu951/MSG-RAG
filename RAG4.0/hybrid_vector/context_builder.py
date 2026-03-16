def build_context(chunks, max_chars= 4000):
    context= ""

    for chunk in chunks:
        block = f"\n{chunk}\n"

        if len(context) + len(block) > max_chars:
            break
        context += block

    return context