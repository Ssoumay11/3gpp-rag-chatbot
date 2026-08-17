from dataclasses import dataclass


@dataclass(frozen=True)
class ParserConfig:
    """
    Configuration for structure-aware 3GPP PDF parsing.
    """

    llamaparse_result_type: str = "markdown"

    # LlamaParse settings
    llamaparse_language: str = "en"
    llamaparse_num_workers: int = 2

    # Unstructured settings
    unstructured_strategy: str = "hi_res"
    unstructured_infer_tables: bool = True

    # Output
    save_page_level_output: bool = True