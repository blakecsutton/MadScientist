# Overview #

**MadScientist** is a Django application for a idea bank, developed with Django 1.4 and compatible with 1.3 and above. With this application, you can quickly record ideas that aren’t necessarily visual, in a way that optimizes browsing and information retrieval later on. After all, the purpose of an idea bank is to inspire you later, when you’re out of ideas.

What makes it easy to both add and browse ideas is faceted tagging: a relatively small number of tags are organized into distinct, thoughtful categories known as facets, which are each meant to represent orthogonal aspects of an idea. For example, I use facets called Medium (type of material) and Skill to classify ideas like sewing a quilt (Medium: fabric, Skills: quilting, sewing).

In the admin interface, available tags are represented as columns of checkboxes organized by facet, so you can quickly check off any tags which apply to the current idea. Tags are then applied to the idea in the database, so it's easy to search and filter by tag. 

## Models ##

It's a pretty simple application with only three models: Idea, Facet, and Tag. Ideas have zero or more tags associated with them, Facets have zero or more Tags associated with them, and Tags may have zero or one associated Facet. Tags are restricted to one Facet because Facets are intended to serve as categories of tags, and thus tags should only belong in one category. 

If you find you are having trouble figuring out what Facet a Tag should belong to, then one of them needs more thought. A good classification is straightforward and unambiguous: see [this link](http://www.miskatonic.org/library/facet-web-howto.html) for an article on how to design faceted classifications which I found extremely useful.

## Admin widget and Dojo editor ##

This application uses a custom widget called FacetedColumnCheckboxSelectMultiple, which inherits from CheckboxSelectMultiple. Its purpose is to visually group available Tags into columns by Facet. The code for this can founds in widgets.py.

It also uses the Dojo editor plugin to provide rich text support in the admin interface when adding ideas. The code for this can be found in admin.py, and the relevant CSS and JavaScript files are expected to be in an "editor" subfolder somewhere that Django knows to look for static files.