import nltk as nl
# import httplib2
# import beautifulsoup as bs

stopwords = nl.corpus.stopwords.words('english')
stopwords = stopwords + [",",";",":","?","=","+","."]

def tokenize_title (title):
	tokens = nl.tokenize.word_tokenize(title) #nl.tag.pos_tag(nl.tokenize.word_tokenize(title))
	words = [w for w in tokens if w.lower() not in stopwords]
	return words


# def has_good_punctuation(p):
# 	periods = len(p.split('.'))-1
# 	semicolons = len(p.split(';'))-1
# 	commas = len(p.split(','))-1
# 	# 1 punctuation per 12 words, at least
# 	if len(p)>0:
# 		# puts "==============PARAGRAPH=============="
# 		# puts p
# 		# puts "============END PARAGRAPH============"
# 		# puts "punctuation per word : (#{(periods+semicolons+commas).to_f/p.split().length.to_f})"
# 		if float(periods+semicolons+commas)/float(len(p.split())>1.0/50.0:
# 			# puts "=========keeping this paragraph========="
# 			return True
# 		else:
# 			return False
# 	else:
# 		return False

# def has_high_link_density(p):
# 	links = float(len(p.select('a')))
# 	links_text = p.select('a')
# 	text_without_links = len(p.get_text())-len(links_text.get_text())
# 	if len(p.get_text())>0:
# 		# 1 link for 3 words, at most
# 		# puts "links per word : (#{links/p.text.split().length.to_f})"
# 		# puts "nonlinking text vs total : (#{text_without_links.to_f/p.text.length.to_f})"
# 		if links/p.text.split().length.to_f>1.0/3.0
# 			if float(text_without_links)/float(len(p.get_text()))>0.5:
# 				return False
# 			else:
# 				return True
# 		else:
# 			return False
# 	else:
# 		return True

# def has_no_div_children(div)
# 	for child in div.findChildren():
# 		if child.name == 'div':
# 			return False
# 	return True

# def superset_text_is_junk(superset,subset):
# 	# puts "checking superset"
# 	superset_text = superset.get_text()
# 	subset_text = subset.get_text()
# 	superset_text = superset_text.replace(subset_text,'')
# 	if has_good_punctuation(superset_text) and float(len(superset_text))/float(len(subset_text))>0.1:
# 		True
# 	else:
# 		False

# def keep_childmost_meaningful_els(keptnodes,pieces):
# 	pieces_to_toss = []
# 	nodes_to_toss = []
# 	for node in keptnodes:
# 		parent = node.parent
# 		while parent.class != Nokogiri::HTML::Document
# 			if ([parent] & keptnodes).length>0:
# 				if superset_text_is_junk(parent,node)
# 					nodes_to_toss << parent
# 					pieces_to_toss << pieces[keptnodes.index(parent)]
# 				else
# 					nodes_to_toss << node
# 					pieces_to_toss << pieces[k]
# 				end
# 			end
# 			parent = parent.parent()
# 		end
# 	end
# 	keptnodes = keptnodes-nodes_to_toss
# 	pieces = pieces-pieces_to_toss
# 	[keptnodes,pieces]

# def keep_friendliest_els(keptnodes,pieces):
# 	average_nesting = 0
# 	# puts "we're good"
# 	for piece in pieces:
# 		average_nesting += piece['nesting']
# 	average_nesting = average_nesting.to_f/pieces.count.to_f
# 	pieces_to_toss = []
# 	nodes_to_toss = []
# 	pieces.each_with_index do |piece, k|
# 		intersect = keptnodes & keptnodes[k].parent().children().to_a
# 		if (piece[:nesting]-average_nesting).abs<2:
# 			if intersect.count == 1 and pieces.count > 2:
# 				nodes_to_toss << keptnodes[k]
# 				pieces_to_toss << piece
# 				# puts "This paragraph is a loner:\n#{piece[:text]}"
# 			end
# 		elsif intersect.count>1
# 			# I'm part of gang
# 		else:
# 			nodes_to_toss << keptnodes[k]
# 			pieces_to_toss << piece
# 			# puts "This paragraph (#{piece[:nesting]}) does not have the right nesting (#{average_nesting}), and is a loner:\n#{piece[:text]}"
# 	[keptnodes,pieces]

# def description_extract(page,originalurl)
# 	extract = ""
# 	pieces = []
# 	keptnodes = []
# 	begin
# 		page.css('a','A').each do |link|
# 			if link["href"]
# 				begin
# 					link["href"] = URI.join(originalurl, URI.escape(link["href"]).to_s).to_s
# 				rescue => e
# 					puts e
# 					link["href"] = ""
# 				end
# 			end
# 		end
# 		page.css('script').remove()
# 		if page.css("p",'P').first
# 			page.css('p','P').each do |p|
# 				if has_high_link_density(p)
# 				elsif has_good_punctuation(p.text)
# 					# puts "text length : (#{p.text.length} chars)"
# 					if p.text.length>50
# 						# puts "text length > 50 : TRUE"
# 						nesting = 0
# 						parent = p
# 						while parent
# 							if parent.class == Nokogiri::HTML::Document
# 								break
# 							else
# 								parent = parent.parent()
# 								nesting +=1
# 							end
# 						end
# 						# puts "nesting : (#{nesting})"
# 						# puts "paragraph => \n(#{p.text})"
# 						pieces << {:text => p.inner_html+"\n", :nesting => nesting}
# 						keptnodes << p
# 					end
# 				else
# 				end
# 			end
# 		end
# 		if pieces.length>0
# 			o = keep_friendliest_els(keptnodes,pieces)
# 			keptnodes = o[0]
# 			pieces = o[1]
# 			# puts "looking at childmost els"
# 			# o = keep_childmost_meaningful_els(keptnodes,pieces)
# 			# keptnodes = o[0]
# 			# pieces = o[1]
# 			# puts "looking at friendliest els"
# 			if pieces.length>0
# 				pieces.each {|p| extract += p[:text]}
# 			else
# 				extract = ""
# 			end
# 		else
# 			# puts "GONNA USE DIVS TOO"
# 			if page.css("div").first
# 				page.css('div').each do |div|
# 					if has_high_link_density(div)
# 					elsif has_good_punctuation(div.text)
# 						if div.text.length>50
# 							nesting = 0
# 							parent = div
# 							while parent
# 								if parent.class == Nokogiri::HTML::Document
# 									break
# 								else
# 									parent = parent.parent()
# 									nesting +=1
# 								end
# 							end
# 							# puts "nesting : (#{nesting})"
# 							# puts "paragraph => \n(#{div.text})"
# 							pieces << {:text => div.inner_html+"\n", :nesting => nesting}
# 							keptnodes << div
# 						end
# 					end
# 				end
# 				if pieces.length>0
# 					o = keep_friendliest_els(keptnodes,pieces)
# 					keptnodes = o[0]
# 					pieces = o[1]
# 					# puts "looking at childmost els"
# 					# o = keep_childmost_meaningful_els(keptnodes,pieces)
# 					# keptnodes = o[0]
# 					# pieces = o[1]
# 					# puts "looking at friendliest els"
# 					if pieces.length>0
# 						pieces.each {|p| extract += p[:text]}
# 					else
# 						extract = ""
# 					end
# 				end
# 			end
# 		end
# 		extract = Sanitize.clean((extract.force_encoding 'utf-8'), Sanitize::Config::BASIC).strip.squeeze_line_breaks
# 		extract = extract[0..64999]
# 	rescue
# 		extract = ""
# 	end
# 	page = nil
# 	extract
# end