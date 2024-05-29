import pandas as pd
from forms.interface_parser import InterfaceParser

class GenericParser(InterfaceParser):
    def __init__(self, table: pd.DataFrame,
		generate_title_id = lambda tags: 1,
		generate_indicator_count = lambda title, subindicator_names: 2,
		generate_description = lambda title, subindicator_names, statform, indicator_names: "TBA",
		reference = None,
        statform = "-"):
        super().__init__(table, generate_title_id, generate_indicator_count, generate_description, reference, statform)
        pass

    def retrieve_tags(self):
        """Returns (tag_row_count, [tags]) from header"""
        find_first = lambda search_string: next((index for index, row in self.table.iterrows() if row.astype(str).str.contains(search_string).any()), 10000)
        self.header_bottom = min(find_first("№ строки"), find_first("Наименование"))
        for i in range(5):
            if isinstance(self.table.iloc[0, i], str):
                table_tags = list(self.table.iloc[0:self.header_bottom, i])
                break
        return (len(table_tags), table_tags)
    
    def retrieve_subindicators(self):
        """Returns (subindicator_row_count, [[subindicator_1], [subindicator_2]...]). Table *HAS* to be without table tags above"""
        def fix(lst):
            cleaned_list = [str(v) if isinstance(v, float) else v for v in lst]
            return [v for i, v in enumerate(cleaned_list) if i == 0 or v != cleaned_list[i - 1]]

        self.subindicator_bottom = next((i for i, value in enumerate(self.table.iloc[:, 0]) if (value == '1') or (value == 1) or (value == 1.0)), 0)
        subindicators_df = self.table.iloc[self.header_bottom:self.subindicator_bottom+1]
        subindicators_df = subindicators_df.replace('', float('NaN')).dropna(axis=1, how='all')
        subindicators = [fix(subindicators_df[col].tolist()) for col in subindicators_df.columns]

        return (self.subindicator_bottom - self.header_bottom, subindicators)
    
    def retrieve_indicators(self):
        """Returns [[indicator_1], [indicator_2], ...]"""
        return self.table.iloc[self.subindicator_bottom+1:,0:self.indicator_count].values.tolist()
    
    def retrieve_values(self):
        return self.table.iloc[self.subindicator_bottom+1:, self.indicator_count:len(self.subindicators)].reset_index(drop = True).values.tolist()