
#ifndef _PARSER_NODE_H_
#define _PARSER_NODE_H_

#include<stdio.h>
#include<stdlib.h>
#include<stdint.h>

struct ParserNode;
struct ParserNodeLocation;

// ==========


typedef struct ParserNode {
	int32_t references;
	int32_t _unused_;

	// name
	char *name;

	char *slicePtr;
	struct ParserNodeLocation location;

	int32_t capacity;
	int32_t length;
	struct ParserNode *children[];

} ParserNode;

typedef struct ParserNodeLocation {
	int32_t row,col;
	int64_t idx;
	int32_t endRow,endCol;
	int64_t endIdx;
	struct ParserNode *data;
} ParserNodeLocation;

// ======


ParserNodeLocation parser_location_new(void);
void    parser_location_incr(ParserNodeLocation *loc);
void    parser_location_incrLine(ParserNodeLocation *loc);
void    parser_location_setRange(ParserNodeLocation *range,ParserNodeLocation *end);
int64_t parser_location_getIndex(ParserNodeLocation *loc);
ParserNodeLocation parser_location_fromNode(ParserNode *node);

ParserNode *parser_node_new(uint8_t *data,ParserNodeLocation *loc);
ParserNode *parser_node_fromRange(uint8_t *data,ParserNodeLocation *loc,int64_t next);
void parser_node_free(ParserNode *node);
void parser_node_appendChild(ParserNode **node,ParserNode *child);
void parser_node_appendChildrenOf(ParserNode **node,ParserNode *child);


// ======

ParserNodeLocation parser_location_new(void){
	ParserNodeLocation loc = {0};
	loc.row = 1;
	loc.col = 1;
	loc.endRow = 1;
	loc.endCol = 1;
	return loc;
}
void parser_location_incr(ParserNodeLocation *loc){
	loc->col++;
	loc->idx++;
	loc->endIdx = loc->row;
	loc->endCol = loc->col;
}
void parser_location_incrLine(ParserNodeLocation *loc){
	loc->col = 1;
	loc->idx++;
	loc->row++;
	loc->endIdx = loc->row;
	loc->endCol = loc->col;
	loc->endRow = loc->row;
}
void parser_location_setRange(ParserNodeLocation *range,ParserNodeLocation *end){
	range->endIdx = end->idx;
	range->endCol = end->col;
	range->endRow = end->row;
}
int64_t parser_location_getIndex(ParserNodeLocation *loc){
	return loc->idx;
}
ParserNodeLocation parser_location_fromNode(ParserNode *node){
	ParserNodeLocation pnl = node->location;
	pnl.idx = pnl.endIdx;
	pnl.col = pnl.endCol;
	pnl.row = pnl.endRow;
	return pnl;
}

ParserNode *parser_node_new(uint8_t *data,ParserNodeLocation *loc){
	const int32_t initCapacity = 4;
	size_t sz = sizeof(ParserNode);
	sz += sizeof(ParserNode*) * initCapacity;
	ParserNode *n = malloc(sz); 
	n->references = 0;
	n->name = NULL;
	n->slicePtr = data;
	n->location = *loc;
	n->capacity = initCapacity;
	n->length = 0;

	return n;
}
ParserNode *parser_node_fromRange(uint8_t *data,ParserNodeLocation *loc,int64_t next){
	ParserNode *n = parser_node_new(data,loc); 
	n->location.endIdx = next;
	n->location.endRow = n->location.row;
	n->location.endCol = n->location.col;
	for(int32_t i = loc.idx;i <= next;i++){
		n->location.endCol++;
		if(data[i] != '\n')continue;
		n->location.endRow++;
		n->location.endCol = 1;
	}
	return n;

}
void parser_node_free(ParserNode *node){
	if(node == NULL)return;
	for(int32_t idx = 0;idx < node->length;idx++){
		parser_node_free(node->children[idx]);
	}
	free(node);
}
void parser_node_appendChild(ParserNode **node,ParserNode *child){
	ParserNode *capNode = *node;
	if(capNode->length >= capNode->capacity){
		capNode->capacity *= 2;
		size_t sz = capNode->capacity * sizeof(ParserNode*);
		sz += sizeof(ParserNode);
		*node = realloc(capNode,sz);
		capNode = *node;
	}
	capNode->children[capNode->length] = child;
	capNode->length++;
}
void parser_node_appendChildrenOf(ParserNode **node,ParserNode *child){
	for(int32_t idx = 0;idx < child->length;idx++){
		parser_node_appendChild(node,child->children[idx]);
		child->children[idx] = NULL;
	}
}


#endif
