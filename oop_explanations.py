def get_oop_explanations() -> str:
    return (
        "OOP Concepts used in this app:\n\n"
        "1) Inheritance: BaseModelHandler is a base class; TextModelHandler, "
        "ImageModelHandler, and AudioModelHandler inherit and override run().\n\n"
        "2) Polymorphism: ModelManager.run() calls .run() on different handler types "
        "with the same interface, producing type-appropriate behavior.\n\n"
        "3) Encapsulation: Each handler encapsulates model loading and execution, "
        "hiding pipeline details from the GUI layer. The AppGUI class encapsulates UI state.\n\n"
        "4) Method Overriding: Subclasses override BaseModelHandler.run() and (optionally) _build().\n\n"
        "5) Decorators: @timed and @safe_run wrap methods to add cross-cutting concerns "
        "(timing scaffold, error handling) without changing core logic.\n"
    )
