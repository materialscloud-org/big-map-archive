import { parametrize } from "react-overridable";
import {
  ContribSearchAppFacets,
} from "@js/invenio_search_ui/components";

export const BMAContribSearchAppFacetsWithConfig = parametrize(ContribSearchAppFacets, {
  aggs: [],
  toggle: true,
});