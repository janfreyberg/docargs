BRANCH_NAME=$(git symbolic-ref -q HEAD)
BRANCH_NAME=${BRANCH_NAME##refs/heads/}
BRANCH_NAME=${BRANCH_NAME:-HEAD}

gh-pages:
	git checkout gh-pages
	rm -rf *
	git checkout $(BRANCH_NAME) docs docargs
	# make -C docs/ api html
	make -C docs/ html
	mv ./docs/_build/html/* ./
	rm -rf docs docargs
	echo "baseurl: /docargs" > _config.yml
	touch .nojekyll
	git add -A
	git commit -m "publishing updated docs..."
	git push origin gh-pages
	# switch back
	git checkout master


.PHONY: gh-pages
