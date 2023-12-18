import React from "react";
import {
    Card,
    Checkbox,
    Icon,
    Popup
} from "semantic-ui-react";
import PropTypes from "prop-types";

export const BMASearchFiltersToggleElement = ({
                                                  updateQueryFilters,
                                                  userSelectionFilters,
                                                  filterValue,
                                                  label,
                                                  title,
                                              }) => {
    const _isChecked = (userSelectionFilters) => {
        const isFilterActive =
            userSelectionFilters.filter((filter) => filter[0] === filterValue[0]).length > 0;
        return isFilterActive;
    };

    const onToggleClicked = () => {
        updateQueryFilters(filterValue);
    };

    var isChecked = _isChecked(userSelectionFilters);

    title = "Versions";
    label = "All versions"

    return (
        <Card className="borderless facet">
            <Card.Content className="flex-center">
                <Card.Header as="h2" className="mb-0">{title}</Card.Header>
                <Popup
                    trigger={<Icon className="ml-5" name="info circle flex-center"/>}
                    content={"By default, only the latest shared version of an entry is displayed. Toggle the switch to view all shared versions."}
                />
            </Card.Content>
            <Card.Content>
                <Checkbox
                    toggle
                    label={<label aria-hidden="true">{label}</label>}
                    name="versions-toggle"
                    aria-label={label}
                    onClick={onToggleClicked}
                    checked={isChecked}
                />
            </Card.Content>
        </Card>
    );
};

BMASearchFiltersToggleElement.propTypes = {
    title: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    filterValue: PropTypes.array.isRequired,
    userSelectionFilters: PropTypes.array.isRequired,
    updateQueryFilters: PropTypes.func.isRequired,
};